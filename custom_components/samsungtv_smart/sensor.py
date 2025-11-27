"""Samsung Frame TV Art Mode sensor entity."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_TOKEN
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api.art import SamsungTVAsyncArt
from .const import (
    CONF_WS_NAME,
    DATA_ART_API,
    DATA_CFG,
    DEFAULT_PORT,
    DOMAIN,
    WS_PREFIX,
)

_LOGGER = logging.getLogger(__name__)

# Update interval for the Frame Art sensor
SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Samsung Frame Art sensor from config entry."""
    config = hass.data[DOMAIN][entry.entry_id][DATA_CFG]
    host = config[CONF_HOST]
    port = config.get(CONF_PORT, DEFAULT_PORT)
    token = config.get(CONF_TOKEN)
    ws_name = config.get(CONF_WS_NAME, "HomeAssistant")
    
    # Get device name from config or entry title, fallback to host
    device_name = config.get(CONF_NAME) or entry.title or host
    
    session = async_get_clientsession(hass)
    
    # Create the Art API instance
    art_api = SamsungTVAsyncArt(
        host=host,
        port=port,
        token=token,
        session=session,
        timeout=5,
        name=f"{WS_PREFIX} {ws_name} Art",
    )
    
    # Quick check if Frame TV is supported (with short timeout)
    try:
        async with asyncio.timeout(5):
            is_supported = await art_api.supported()
    except asyncio.TimeoutError:
        _LOGGER.debug("Timeout checking Frame TV support for %s", host)
        is_supported = False
    except Exception as ex:
        _LOGGER.debug("Frame TV support check failed: %s", ex)
        is_supported = False
    
    if not is_supported:
        _LOGGER.info("Frame TV art mode not supported on %s", host)
        return
    
    # Create www/frame_art directory if it doesn't exist
    import os
    www_path = hass.config.path("www", "frame_art")
    try:
        os.makedirs(www_path, exist_ok=True)
        _LOGGER.debug("Frame Art directory ready: %s", www_path)
    except Exception as ex:
        _LOGGER.warning("Could not create frame_art directory: %s", ex)
    
    # Store art_api in hass.data for sharing with media_player
    hass.data[DOMAIN][entry.entry_id][DATA_ART_API] = art_api
    
    # Create the coordinator
    coordinator = FrameArtCoordinator(hass, art_api, entry)
    
    # Create the sensor entity immediately (don't wait for first refresh)
    # The coordinator will update data in the background
    async_add_entities([
        FrameArtSensor(coordinator, entry, art_api, device_name),
    ])
    
    # Schedule first refresh in background (non-blocking)
    hass.async_create_background_task(
        coordinator.async_request_refresh(),
        f"frame_art_initial_refresh_{entry.entry_id}",
    )


class FrameArtCoordinator(DataUpdateCoordinator):
    """Coordinator for Frame Art data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        art_api: SamsungTVAsyncArt,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"Frame Art {entry.title}",
            update_interval=SCAN_INTERVAL,
        )
        self._art_api = art_api
        self._entry = entry
        self._hass = hass
        self._last_content_id: str | None = None
        # Disabled by default - can be enabled manually via service
        # Thumbnail fetching can be slow/unreliable on some TV models
        self._thumbnail_fetch_enabled = False
        self._thumbnail_failures = 0

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the Frame TV."""
        data = {
            "art_mode": None,
            "current_artwork": None,
            "artwork_count": None,
            "slideshow_status": None,
            "api_version": None,
            "current_thumbnail_url": None,
        }
        
        try:
            # Get art mode status with timeout
            try:
                async with asyncio.timeout(8):
                    art_mode = await self._art_api.get_artmode()
                    data["art_mode"] = art_mode
            except asyncio.TimeoutError:
                _LOGGER.debug("Timeout getting art mode status")
            except Exception as ex:
                _LOGGER.debug("Error getting art mode: %s", ex)
            
            # Get current artwork with timeout
            content_id = None
            try:
                async with asyncio.timeout(8):
                    current = await self._art_api.get_current()
                    if current:
                        content_id = current.get("content_id")
                        data["current_artwork"] = {
                            "content_id": content_id,
                            "category_id": current.get("category_id"),
                            "matte_id": current.get("matte_id"),
                        }
            except asyncio.TimeoutError:
                _LOGGER.debug("Timeout getting current artwork")
            except Exception as ex:
                _LOGGER.debug("Error getting current artwork: %s", ex)
            
            # Only fetch thumbnail if:
            # - Thumbnail fetching is enabled
            # - We have a content_id
            # - Content has changed OR we don't have a thumbnail yet
            if (
                self._thumbnail_fetch_enabled
                and content_id
                and (content_id != self._last_content_id or not self._has_current_thumbnail())
            ):
                # Schedule thumbnail fetch as background task (non-blocking)
                self._hass.async_create_background_task(
                    self._fetch_and_save_thumbnail(content_id),
                    f"frame_art_thumbnail_{content_id}",
                )
                self._last_content_id = content_id
            
            # If we have a saved thumbnail, use it
            if self._has_current_thumbnail():
                data["current_thumbnail_url"] = "/local/frame_art/current.jpg"
            
            # Get artwork count (less frequently, only if art_mode is on)
            if data["art_mode"] == "on":
                try:
                    async with asyncio.timeout(15):
                        artwork_list = await self._art_api.available()
                        data["artwork_count"] = len(artwork_list) if artwork_list else 0
                except asyncio.TimeoutError:
                    _LOGGER.debug("Timeout getting artwork list")
                except Exception as ex:
                    _LOGGER.debug("Error getting artwork list: %s", ex)
            
            # Get slideshow status with timeout
            try:
                async with asyncio.timeout(8):
                    slideshow = await self._art_api.get_slideshow_status()
                    if slideshow:
                        data["slideshow_status"] = slideshow.get("value", "off")
            except asyncio.TimeoutError:
                _LOGGER.debug("Timeout getting slideshow status")
            except Exception as ex:
                _LOGGER.debug("Error getting slideshow status: %s", ex)
                
        except Exception as ex:
            _LOGGER.warning("Error updating Frame Art data: %s", ex)
            # Don't raise UpdateFailed, just return partial data
            
        return data

    def _has_current_thumbnail(self) -> bool:
        """Check if current thumbnail file exists."""
        import os
        www_path = self._hass.config.path("www", "frame_art", "current.jpg")
        return os.path.isfile(www_path)

    async def _fetch_and_save_thumbnail(self, content_id: str) -> None:
        """Fetch and save thumbnail in background (non-blocking)."""
        try:
            async with asyncio.timeout(20):  # Longer timeout for thumbnails
                thumbnail_data = await self._art_api.get_thumbnail(content_id)
                if thumbnail_data:
                    import os
                    www_path = self._hass.config.path("www", "frame_art")
                    
                    def _write_thumbnails():
                        os.makedirs(www_path, exist_ok=True)
                        
                        # Save as current.jpg
                        file_path = os.path.join(www_path, "current.jpg")
                        with open(file_path, "wb") as f:
                            f.write(thumbnail_data)
                        
                        # Also save with content_id name for gallery
                        content_file = f"{content_id.replace(':', '_')}.jpg"
                        content_path = os.path.join(www_path, content_file)
                        with open(content_path, "wb") as f:
                            f.write(thumbnail_data)
                        
                        return file_path, content_path
                    
                    # Run file I/O in executor to avoid blocking
                    await self._hass.async_add_executor_job(_write_thumbnails)
                    
                    _LOGGER.debug("Saved thumbnail for %s", content_id)
                    self._thumbnail_failures = 0
                    
                    # Trigger state update
                    self.async_set_updated_data(self.data)
        except asyncio.TimeoutError:
            self._thumbnail_failures += 1
            _LOGGER.debug(
                "Timeout fetching thumbnail for %s (failure %d)",
                content_id,
                self._thumbnail_failures,
            )
            # Disable thumbnail fetching after 3 consecutive failures
            if self._thumbnail_failures >= 3:
                _LOGGER.info(
                    "Disabling automatic thumbnail fetch after %d failures. "
                    "Use art_get_thumbnail service to fetch manually.",
                    self._thumbnail_failures,
                )
                self._thumbnail_fetch_enabled = False
        except Exception as ex:
            _LOGGER.debug("Error fetching thumbnail for %s: %s", content_id, ex)


class FrameArtSensor(CoordinatorEntity, SensorEntity):
    """Sensor entity for Samsung Frame TV Art Mode."""

    _attr_icon = "mdi:image-frame"

    def __init__(
        self,
        coordinator: FrameArtCoordinator,
        entry: ConfigEntry,
        art_api: SamsungTVAsyncArt,
        device_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._art_api = art_api
        self._attr_unique_id = f"{entry.entry_id}_frame_art"
        # Use explicit name instead of has_entity_name to avoid "None" prefix
        self._attr_name = f"{device_name} Frame Art"
        self._last_service_result: dict[str, Any] | None = None
        
        # Device info to link with the main TV entity
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def native_value(self) -> str | None:
        """Return the current art mode status."""
        if self.coordinator.data:
            return self.coordinator.data.get("art_mode")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attrs = {}
        
        if self.coordinator.data:
            data = self.coordinator.data
            
            # Art mode status
            if data.get("art_mode") is not None:
                attrs["art_mode_status"] = data["art_mode"]
            
            # Current artwork details
            if data.get("current_artwork"):
                current = data["current_artwork"]
                attrs["current_content_id"] = current.get("content_id")
                attrs["current_category_id"] = current.get("category_id")
                attrs["current_matte_id"] = current.get("matte_id")
            
            # Current thumbnail URL (for Lovelace)
            if data.get("current_thumbnail_url"):
                attrs["current_thumbnail_url"] = data["current_thumbnail_url"]
            
            # Artwork count
            if data.get("artwork_count") is not None:
                attrs["artwork_count"] = data["artwork_count"]
            
            # Slideshow status
            if data.get("slideshow_status") is not None:
                attrs["slideshow_status"] = data["slideshow_status"]
            
            # API version
            if data.get("api_version") is not None:
                attrs["api_version"] = data["api_version"]
        
        # Thumbnail auto-fetch status
        attrs["thumbnail_auto_fetch"] = self.coordinator._thumbnail_fetch_enabled
        
        # Last service result (for debugging/monitoring service calls)
        if self._last_service_result:
            attrs["last_service_result"] = self._last_service_result
        
        return attrs

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    async def async_set_artmode(self, enabled: bool) -> dict:
        """Enable or disable Art Mode."""
        try:
            await self._art_api.set_artmode(enabled)
            result = {"service": "set_artmode", "success": True, "enabled": enabled}
        except Exception as ex:
            result = {"service": "set_artmode", "error": str(ex)}
        self._last_service_result = result
        await self.coordinator.async_request_refresh()
        return result

    async def async_select_image(
        self,
        content_id: str,
        category_id: str | None = None,
        show: bool = True,
    ) -> dict:
        """Select and display artwork."""
        try:
            await self._art_api.select_image(content_id, category_id, show)
            result = {
                "service": "select_image",
                "success": True,
                "content_id": content_id,
            }
        except Exception as ex:
            result = {"service": "select_image", "error": str(ex)}
        self._last_service_result = result
        await self.coordinator.async_request_refresh()
        return result

    async def async_get_available(self, category_id: str | None = None) -> dict:
        """Get list of available artwork."""
        try:
            artwork_list = await self._art_api.available(category_id)
            result = {
                "service": "get_available",
                "success": True,
                "count": len(artwork_list) if artwork_list else 0,
                "artwork": artwork_list,
            }
        except Exception as ex:
            result = {"service": "get_available", "error": str(ex)}
        self._last_service_result = result
        self.async_write_ha_state()
        return result

    async def async_upload_image(
        self,
        file_path: str,
        matte_id: str | None = None,
        file_type: str = "png",
    ) -> dict:
        """Upload an image to the TV."""
        try:
            content_id = await self._art_api.upload(
                file_path,
                matte=matte_id or "shadowbox_polar",
                file_type=file_type,
            )
            result = {
                "service": "upload_image",
                "success": content_id is not None,
                "content_id": content_id,
            }
        except Exception as ex:
            result = {"service": "upload_image", "error": str(ex)}
        self._last_service_result = result
        await self.coordinator.async_request_refresh()
        return result

    async def async_delete_image(self, content_id: str) -> dict:
        """Delete an uploaded image."""
        try:
            success = await self._art_api.delete(content_id)
            result = {
                "service": "delete_image",
                "success": success,
                "content_id": content_id,
            }
        except Exception as ex:
            result = {"service": "delete_image", "error": str(ex)}
        self._last_service_result = result
        await self.coordinator.async_request_refresh()
        return result

    async def async_set_slideshow(
        self,
        duration: int = 0,
        shuffle: bool = True,
        category_id: int = 2,
    ) -> dict:
        """Configure slideshow settings."""
        try:
            success = await self._art_api.set_slideshow_status(
                duration=duration,
                shuffle=shuffle,
                category=category_id,
            )
            result = {
                "service": "set_slideshow",
                "success": success,
                "duration": duration,
                "shuffle": shuffle,
            }
        except Exception as ex:
            result = {"service": "set_slideshow", "error": str(ex)}
        self._last_service_result = result
        await self.coordinator.async_request_refresh()
        return result

    async def async_change_matte(
        self,
        content_id: str,
        matte_id: str,
    ) -> dict:
        """Change the matte/frame style for artwork."""
        try:
            success = await self._art_api.change_matte(content_id, matte_id)
            result = {
                "service": "change_matte",
                "success": success,
                "content_id": content_id,
                "matte_id": matte_id,
            }
        except Exception as ex:
            result = {"service": "change_matte", "error": str(ex)}
        self._last_service_result = result
        self.async_write_ha_state()
        return result

    async def async_set_photo_filter(
        self,
        content_id: str,
        filter_id: str,
    ) -> dict:
        """Apply a photo filter to artwork."""
        try:
            success = await self._art_api.set_photo_filter(content_id, filter_id)
            result = {
                "service": "set_photo_filter",
                "success": success,
                "content_id": content_id,
                "filter_id": filter_id,
            }
        except Exception as ex:
            result = {"service": "set_photo_filter", "error": str(ex)}
        self._last_service_result = result
        self.async_write_ha_state()
        return result

    async def async_set_favourite(
        self,
        content_id: str,
        status: str = "on",
    ) -> dict:
        """Add or remove artwork from favorites."""
        try:
            success = await self._art_api.set_favourite(content_id, status)
            result = {
                "service": "set_favourite",
                "success": success,
                "content_id": content_id,
                "status": status,
            }
        except Exception as ex:
            result = {"service": "set_favourite", "error": str(ex)}
        self._last_service_result = result
        self.async_write_ha_state()
        return result

    async def async_enable_thumbnail_fetch(self, enabled: bool = True) -> dict:
        """Enable or disable automatic thumbnail fetching.
        
        If thumbnail fetching times out repeatedly, it is automatically disabled.
        Use this method to re-enable it.
        """
        self.coordinator._thumbnail_fetch_enabled = enabled
        self.coordinator._thumbnail_failures = 0
        result = {
            "service": "enable_thumbnail_fetch",
            "success": True,
            "enabled": enabled,
        }
        self._last_service_result = result
        self.async_write_ha_state()
        
        # If enabling, trigger an immediate refresh
        if enabled:
            await self.coordinator.async_request_refresh()
        
        return result

    async def async_get_thumbnail(self, content_id: str) -> dict:
        """Manually fetch and save a thumbnail for a specific artwork."""
        try:
            thumbnail_data = await self._art_api.get_thumbnail(content_id, timeout=30)
            if thumbnail_data:
                import os
                www_path = self.hass.config.path("www", "frame_art")
                
                def _write_thumbnail():
                    os.makedirs(www_path, exist_ok=True)
                    file_name = f"{content_id.replace(':', '_')}.jpg"
                    file_path = os.path.join(www_path, file_name)
                    with open(file_path, "wb") as f:
                        f.write(thumbnail_data)
                    return file_name
                
                file_name = await self.hass.async_add_executor_job(_write_thumbnail)
                
                result = {
                    "service": "get_thumbnail",
                    "success": True,
                    "content_id": content_id,
                    "thumbnail_url": f"/local/frame_art/{file_name}",
                    "size": len(thumbnail_data),
                }
            else:
                result = {
                    "service": "get_thumbnail",
                    "success": False,
                    "content_id": content_id,
                    "error": "No thumbnail data received",
                }
        except Exception as ex:
            result = {
                "service": "get_thumbnail",
                "success": False,
                "content_id": content_id,
                "error": str(ex),
            }
        self._last_service_result = result
        self.async_write_ha_state()
        return result
