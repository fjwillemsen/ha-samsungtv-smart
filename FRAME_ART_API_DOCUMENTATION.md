# Samsung Frame TV Art Mode API Documentation

This document describes the Frame TV Art Mode API integration (`art.py`) for the SamsungTV Smart component.

## Overview

The `art.py` module provides complete control over Samsung Frame TV Art Mode features, including artwork management, slideshow configuration, thumbnail retrieval, and display settings.

### Credits

This implementation is based on the work of:
- **xchwarze** - [samsung-tv-ws-api](https://github.com/xchwarze/samsung-tv-ws-api) (art-updates branch)
- **Matthew Garrett** (mjg59) - Original contributions
- **Nick Waterton** - Async reference implementation

Adapted for Home Assistant using `aiohttp` instead of `websockets`.

---

## Features

The Art Mode API provides the following capabilities:

* Get and set Art Mode status (on/off)
* List all available artworks and categories
* Select and display specific artwork
* Download artwork thumbnails for UI display
* Upload custom images to the TV
* Delete uploaded images
* Manage favorites
* Configure slideshow and auto-rotation
* Change matte (frame) styles
* Apply photo filters
* Adjust brightness and color temperature

---

## Architecture

### Main Class: `SamsungTVAsyncArt`

```python
class SamsungTVAsyncArt:
    """Async Samsung Frame TV Art Mode API class using aiohttp."""
```

#### Initialization Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` | `str` | required | TV IP address |
| `port` | `int` | `8001` | WebSocket port (8001=insecure, 8002=secure) |
| `token` | `str \| None` | `None` | Authentication token (required for port 8002) |
| `session` | `aiohttp.ClientSession \| None` | `None` | External HTTP session |
| `timeout` | `int` | `5` | Default timeout in seconds |
| `name` | `str` | `"HomeAssistant"` | Client name for identification |

---

## Available Methods

### Connection Management

#### `open() -> bool`
Establishes WebSocket connection to the TV.

```python
async with SamsungTVAsyncArt(host="192.168.1.100") as art:
    # Connection established automatically
    pass
```

#### `close() -> None`
Properly closes the WebSocket connection.

#### `is_connected -> bool`
Property indicating connection state.

---

### Art Mode Control

#### `get_artmode() -> str | None`
Gets current Art Mode status.

**Returns**: `"on"`, `"off"`, or `None`

#### `set_artmode(mode: str | bool) -> bool`
Enables or disables Art Mode.

```python
await art.set_artmode(True)   # Enable
await art.set_artmode("off")  # Disable
```

---

### Artwork Management

#### `get_artmode_status() -> dict | None`
Gets complete Art Mode state including currently displayed artwork.

**Returns**:
```python
{
    "content_id": "MY_F0001",
    "category_id": "MY-C0004",
    "matte_id": "shadowbox_polar",
    "portrait_matte_id": "flexible_polar",
    "content_type": "mobile"  # or "server" for Art Store
}
```

#### `get_current_artwork() -> dict | None`
Gets detailed information about currently displayed artwork.

#### `get_content_list(category: str | None = None) -> list`
Lists all available artworks.

**Parameters**:
- `category`: Filter by category (e.g., `"MY-C0004"` for Favorites)

**Returns**: List of artworks with metadata

#### `get_category_list() -> list`
Gets available categories.

**Typical categories**:
| ID | Description |
|----|-------------|
| `MY-C0002` | My Photos |
| `MY-C0004` | Favorites |
| `MY-C0008` | All |

#### `select_image(content_id: str, category: str | None = None, show: bool = True) -> bool`
Selects and displays an artwork.

```python
await art.select_image("MY_F0001", show=True)
```

---

### Thumbnail Download

#### `get_thumbnail(content_id: str) -> bytes | None`
Downloads artwork thumbnail.

**Behavior**:
1. For Art Store images (SAM-S*): Warm-up via `get_content_list`
2. Tries `get_thumbnail_list` first (better 2024 TV compatibility)
3. Falls back to simple `get_thumbnail` on failure

**⚠️ Known Limitation**: Samsung Art Store images (SAM-S*) are DRM-protected and typically return error `-1`. Only personal images (MY_F*) work reliably.

```python
thumbnail = await art.get_thumbnail("MY_F0001")
if thumbnail:
    with open("thumb.jpg", "wb") as f:
        f.write(thumbnail)
```

#### `get_thumbnail_list(content_ids: list[str]) -> dict`
Gets connection info for downloading multiple thumbnails.

---

### Image Upload

#### `upload(file, matte, portrait_matte, file_type, date, timeout) -> str | None`
Uploads a new image to the TV.

**Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file` | `str \| bytes` | required | File path or binary data |
| `matte` | `str` | `"shadowbox_polar"` | Landscape frame style |
| `portrait_matte` | `str` | `"shadowbox_polar"` | Portrait frame style |
| `file_type` | `str` | `"png"` | File type (png, jpg) |
| `date` | `str \| None` | `None` | Image date (EXIF format) |
| `timeout` | `int` | `30` | Timeout in seconds |

**Returns**: `content_id` of uploaded image or `None`

```python
content_id = await art.upload(
    "/path/to/image.jpg",
    matte="flexible_black",
    portrait_matte="flexible_black"
)
```

#### `delete(content_id: str) -> bool`
Deletes an uploaded image.

#### `delete_list(content_ids: list[str]) -> bool`
Deletes multiple images.

---

### Favorites

#### `set_favourite(content_id: str, status: str = "on") -> bool`
Adds or removes artwork from favorites.

```python
await art.set_favourite("MY_F0001", "on")   # Add
await art.set_favourite("MY_F0001", "off")  # Remove
```

---

### Matte (Frame) Styles

#### `get_matte_list(include_color: bool = False) -> list | tuple`
Gets available matte styles.

**Common matte styles**:
- `none` - No frame
- `shadowbox_polar` - White shadowbox
- `shadowbox_black` - Black shadowbox
- `flexible_polar` - White flexible
- `modernthin_neutral` - Neutral modern thin

#### `change_matte(content_id, matte_id, portrait_matte) -> bool`
Changes artwork frame style.

```python
await art.change_matte(
    "MY_F0001",
    matte_id="shadowbox_black",
    portrait_matte="shadowbox_black"
)
```

---

### Photo Filters

#### `get_photo_filter_list() -> list[str]`
Lists available filters.

#### `set_photo_filter(content_id: str, filter_id: str) -> bool`
Applies a filter to an image.

---

### Display Settings

#### `get_brightness() -> dict | None`
Gets current brightness.

#### `set_brightness(value: int) -> bool`
Sets brightness (0-100).

**⚠️ Note**: May not work on 2024+ models (they use automatic sensor).

#### `get_color_temperature() -> dict | None`
Gets color temperature.

#### `set_color_temperature(value: int) -> bool`
Sets color temperature.

#### `get_artmode_settings(setting: str = "") -> dict | list | None`
Gets all Art Mode settings or a specific setting.

---

### Slideshow / Auto Rotation

#### `get_slideshow_status() -> dict | None`
Gets slideshow settings.

#### `set_slideshow_status(duration, shuffle, category) -> bool`
Configures slideshow.

**Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `duration` | `int` | `0` | Duration in minutes (0 = disabled) |
| `shuffle` | `bool` | `True` | Random playback |
| `category` | `int` | `2` | Category (2 = My Photos, 4 = Favorites) |

#### `get_auto_rotation_status() -> dict | None`
Gets auto rotation settings.

#### `set_auto_rotation_status(duration, shuffle, category) -> bool`
Configures auto rotation.

---

## Implementation Changes

### 1. Inverted Method Order for `get_thumbnail`

**Before**:
```
get_thumbnail → (10s timeout) → get_thumbnail_list
```

**After**:
```
get_thumbnail_list → (failure) → get_thumbnail
```

**Reason**: `get_thumbnail` systematically times out (10s wasted), while `get_thumbnail_list` works for personal images.

### 2. Warm-up for Art Store Images

For SAM-S* images, a `get_content_list` call is made before download attempt:

```python
if content_id.startswith("SAM-"):
    await self._send_art_request({
        "request": "get_content_list",
        "category": "MY-C0004",
    }, timeout=5)
    await asyncio.sleep(0.1)
```

**Hypothesis**: TV needs to "load" Art Store metadata before serving thumbnails.

### 3. Retry with Increasing Delays

For Art Store images failing with `ConnectionResetError` or `IncompleteReadError`:

```python
if content_id.startswith("SAM-") and retry_count < 2:
    await asyncio.sleep(0.5 * (retry_count + 1))  # 0.5s, then 1s
    return await self._get_thumbnail_via_list(content_id, retry_count + 1)
```

**Maximum**: 3 attempts (delays of 0, 0.5s, 1s)

---

## Content Types

| Prefix | Type | content_type | Thumbnail |
|--------|------|--------------|-----------|
| `MY_F*` | Personal images | `mobile` | ✅ Works |
| `SAM-S*` | Samsung Art Store | `server` | ❌ Blocked (DRM) |
| `SAM-*` (no S) | Free Art Store | `server` | ⚠️ Variable |
| Numeric | Ambient Mode | `ambient` | ❌ Not supported |

---

## Error Handling

### Known Error Codes

| Code | Meaning |
|------|---------|
| `-1` | Generic error / DRM / Access denied |
| `timeout` | TV did not respond within timeout |

### Common Exceptions

- `ConnectionResetError`: Ephemeral port closed before connection
- `IncompleteReadError`: Data truncated during transfer
- `TimeoutError`: No response from TV

---

## Usage Example

```python
import asyncio
from art import SamsungTVAsyncArt

async def main():
    async with SamsungTVAsyncArt(
        host="192.168.1.100",
        port=8002,
        token="your_token"
    ) as art:
        # Check Art Mode
        status = await art.get_artmode()
        print(f"Art Mode: {status}")
        
        # List artworks
        content = await art.get_content_list()
        for item in content[:5]:
            print(f"- {item['content_id']}: {item.get('content_type')}")
        
        # Download thumbnail
        if content:
            first_personal = next(
                (c for c in content if c['content_id'].startswith('MY_F')),
                None
            )
            if first_personal:
                thumb = await art.get_thumbnail(first_personal['content_id'])
                if thumb:
                    print(f"Thumbnail: {len(thumb)} bytes")
        
        # Change displayed artwork
        await art.select_image("MY_F0001")
        
        # Configure slideshow
        await art.set_slideshow_status(
            duration=15,  # 15 minutes
            shuffle=True,
            category=4    # Favorites
        )

asyncio.run(main())
```

---

## Home Assistant Integration

### File Structure

```
custom_components/samsungtv_smart/
├── api/
│   └── art.py          # ← This file
├── media_player.py     # Uses SamsungTVAsyncArt
├── sensor.py           # Frame Art attributes sensor
└── services.yaml       # Service definitions
```

### Exposed Home Assistant Services

***Set Artwork***
```yaml
service: samsungtv_smart.frame_art_set_artwork
data:
  entity_id: media_player.samsungtv
  content_id: "MY_F0001"
```

***Get Thumbnail***
```yaml
service: samsungtv_smart.frame_art_get_thumbnail
data:
  entity_id: media_player.samsungtv
  content_id: "MY_F0001"
```

***Upload Image***
```yaml
service: samsungtv_smart.frame_art_upload_image
data:
  entity_id: media_player.samsungtv
  file_path: "/config/www/my_art.jpg"
  matte: "shadowbox_black"
```

***Set Slideshow***
```yaml
service: samsungtv_smart.frame_art_set_slideshow
data:
  entity_id: media_player.samsungtv
  duration: 15
  shuffle: true
  category: 4
```

***Change Matte***
```yaml
service: samsungtv_smart.frame_art_change_matte
data:
  entity_id: media_player.samsungtv
  content_id: "MY_F0001"
  matte_id: "flexible_black"
```

***Set Favorite***
```yaml
service: samsungtv_smart.frame_art_set_favorite
data:
  entity_id: media_player.samsungtv
  content_id: "MY_F0001"
  status: "on"
```

---

## Known Limitations

1. **Art Store Images**: SAM-S* thumbnails are DRM-protected and cannot be downloaded locally via this API.

2. **Brightness on 2024+ Models**: The `set_brightness` command may not work as these models use automatic sensor.

3. **Ephemeral Port**: The download port closes very quickly (~100-200ms). Connection must be immediate.

4. **Token Required**: For secure port (8002), an authentication token is required.

5. **Network Requirements**: TV and Home Assistant must be on the same VLAN. WebSocket connections through different VLANs normally don't work.

---

## Changelog

### v2.0.0 (November 2025)
- Complete rewrite based on xchwarze/samsung-tv-ws-api
- Converted from `websockets` to `aiohttp`
- Added `get_thumbnail_list` support for 2024 TVs
- Implemented warm-up + retry for Art Store images
- Inverted download method order
- Comprehensive documentation

### Issues Resolved
- `AttributeError: _hass` - Fixed
- `blocking call` warnings - Using `async_add_executor_job`
- Systematic timeout on `get_thumbnail` - Inverted method order

---

## References

- [samsung-tv-ws-api (xchwarze)](https://github.com/xchwarze/samsung-tv-ws-api/tree/art-updates)
- [samsung-tv-ws-api (NickWaterton)](https://github.com/NickWaterton/samsung-tv-ws-api)
- [Home Assistant Samsung TV Integration](https://www.home-assistant.io/integrations/samsungtv/)
- [SamsungTV Smart (ollo69)](https://github.com/ollo69/ha-samsungtv-smart)
