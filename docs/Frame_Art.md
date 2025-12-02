# 🖼️ Frame Art Mode - Complete Guide

This guide covers all Frame Art Mode features for Samsung Frame TV integration.

---

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Available Services](#available-services)
- [Sensors and Attributes](#sensors-and-attributes)
- [Configuration Examples](#configuration-examples)
- [Thumbnail Management](#thumbnail-management)
- [Automation Examples](#automation-examples)
- [Troubleshooting](#troubleshooting)

---

## Overview

Frame Art Mode allows you to:
- 🎨 Display artwork when TV is off
- 📸 Manage personal photos and Art Store images
- 🖼️ Change frame styles (mattes)
- 💡 Control brightness levels
- ⭐ Organize favorites
- 🎬 Create slideshows

---

## Requirements

### Hardware
- Samsung Frame TV (2018+ models)
- Tested on: QE55LS03D (2024), QE55LS03B (2023), QE55LS03A (2022)

### Software
- Home Assistant 2023.1+
- SamsungTV Smart integration installed

### Network
- TV and Home Assistant on same network
- Stable connection (wired recommended)

---

## Available Services

### `samsungtv_smart.art_select_image`

Display a specific artwork on Frame TV.

**Parameters:**
```yaml
entity_id: media_player.samsung_frame_tv  # Required
content_id: MY_F0001                      # Required - Artwork ID
show: true                                 # Optional - Show immediately (default: true)
```

**Example:**
```yaml
service: samsungtv_smart.art_select_image
data:
  entity_id: media_player.samsung_frame_tv
  content_id: SAM-S2701
  show: true
```

**Finding Content IDs:**
- Personal photos: `MY_F0001`, `MY_F0002`, etc.
- Art Store: `SAM-S2701`, `SAM-S0700`, etc.
- Check `sensor.samsung_frame_art_list` attributes for all IDs

---

### `samsungtv_smart.art_set_brightness`

Adjust Frame TV brightness (0-100).

**Parameters:**
```yaml
entity_id: media_player.samsung_frame_tv  # Required
brightness: 80                             # Required - 0 to 100
```

**Note:** Brightness value is automatically converted to TV's 0-10 scale.

**Example:**
```yaml
service: samsungtv_smart.art_set_brightness
data:
  entity_id: media_player.samsung_frame_tv
  brightness: 50  # Medium brightness
```

**Typical Values:**
- 100: Maximum (sunny rooms)
- 80: High (morning/daytime)
- 50: Medium (normal use)
- 30: Low (evening)
- 10: Minimum (night)

---

### `samsungtv_smart.art_change_matte`

Change the frame style (matte) around artwork.

**Parameters:**
```yaml
entity_id: media_player.samsung_frame_tv  # Required
matte_id: shadowbox_polar                  # Required - Matte style ID
content_id: MY_F0001                      # Optional - Artwork to apply to
```

**Available Matte Styles:**

**Types:**
- `none` - No matte
- `shadowbox` - Classic frame
- `shadowboxthin` - Thin classic frame
- `shadowboxwide` - Wide classic frame
- `modern` - Modern minimalist
- `modernthin` - Thin modern
- `modernwide` - Wide modern
- `flexible` - Flexible format
- `panoramic` - Panoramic format

**Colors:**
- `black`, `white`, `polar`, `neutral`
- `antique`, `warm`, `sand`, `seafoam`
- `sage`, `burgandy`, `navy`, `apricot`
- `byzantine`, `lavender`, `redorange`

**Format:** `{type}_{color}` (e.g., `shadowbox_polar`, `modern_black`)

**Example:**
```yaml
service: samsungtv_smart.art_change_matte
data:
  entity_id: media_player.samsung_frame_tv
  matte_id: shadowbox_black
  content_id: MY_F0001
```

---

### `samsungtv_smart.art_slideshow`

Start or stop artwork slideshow.

**Parameters:**
```yaml
entity_id: media_player.samsung_frame_tv  # Required
slideshow_type: MY-C0002                   # Optional - Category ID
show: true                                 # Required - true=start, false=stop
```

**Category IDs:**
- `MY-C0002` - Personal photos
- `MY-C0004` - Favorites
- Leave empty for all artwork

**Example:**
```yaml
# Start slideshow with personal photos
service: samsungtv_smart.art_slideshow
data:
  entity_id: media_player.samsung_frame_tv
  slideshow_type: MY-C0002
  show: true

# Stop slideshow
service: samsungtv_smart.art_slideshow
data:
  entity_id: media_player.samsung_frame_tv
  show: false
```

---

### `samsungtv_smart.art_available`

Get list of available artwork (updates sensor).

**Parameters:**
```yaml
entity_id: media_player.samsung_frame_tv  # Required
category_id: MY-C0002                      # Optional - Filter by category
```

**Example:**
```yaml
service: samsungtv_smart.art_available
data:
  entity_id: media_player.samsung_frame_tv
  category_id: MY-C0004  # Get only favorites
```

---

### `samsungtv_smart.art_current`

Get currently displayed artwork information.

**Parameters:**
```yaml
entity_id: media_player.samsung_frame_tv  # Required
```

**Example:**
```yaml
service: samsungtv_smart.art_current
data:
  entity_id: media_player.samsung_frame_tv
```

---

### `samsungtv_smart.art_get_thumbnail`

Download thumbnail for a specific artwork.

**Parameters:**
```yaml
entity_id: media_player.samsung_frame_tv  # Required
content_id: MY_F0001                      # Required - Artwork ID
force_download: false                      # Optional - Re-download if exists
```

**Features:**
- ✅ Automatic directory organization (personal/store/other)
- ✅ Skip if file already exists (unless `force_download: true`)
- ✅ Automatic retry on failure (3 attempts)
- ✅ Base64 removed from entity attributes (saves memory)

**Example:**
```yaml
service: samsungtv_smart.art_get_thumbnail
data:
  entity_id: media_player.samsung_frame_tv
  content_id: SAM-S2701
  force_download: false
```

**Storage Locations:**
- Personal photos: `/config/www/frame_art/personal/MY_F0001.jpg`
- Art Store: `/config/www/frame_art/store/SAM-S2701.jpg`
- Other: `/config/www/frame_art/other/CONTENT_ID.jpg`

---

### `samsungtv_smart.art_get_thumbnails_batch`

Download thumbnails for multiple artworks at once.

**Parameters:**
```yaml
entity_id: media_player.samsung_frame_tv  # Required
favorites_only: false                      # Optional - Only favorites
personal_only: false                       # Optional - Only personal photos
force_download: false                      # Optional - Re-download existing
```

**Performance:**
- First run: ~2 minutes for 40 images
- Subsequent runs: ~2 seconds (skips existing files)
- Success rate: 95%+ with automatic retry

**Example:**
```yaml
# Download all thumbnails (first time setup)
service: samsungtv_smart.art_get_thumbnails_batch
data:
  entity_id: media_player.samsung_frame_tv

# Download only personal photos
service: samsungtv_smart.art_get_thumbnails_batch
data:
  entity_id: media_player.samsung_frame_tv
  personal_only: true

# Force re-download all
service: samsungtv_smart.art_get_thumbnails_batch
data:
  entity_id: media_player.samsung_frame_tv
  force_download: true
```

**Result Format:**
```json
{
  "service": "art_get_thumbnails_batch",
  "total_artworks": 42,
  "downloaded": 40,
  "skipped": 0,
  "failed": 2,
  "downloaded_list": ["MY_F0001", "MY_F0002", ...],
  "skipped_list": [],
  "failed_list": [
    {"content_id": "SAM-S9999", "reason": "Connection timeout"}
  ]
}
```

---

### `samsungtv_smart.set_art_mode`

Enable Art Mode on Frame TV.

**Parameters:**
```yaml
entity_id: media_player.samsung_frame_tv  # Required
```

**Example:**
```yaml
service: samsungtv_smart.set_art_mode
target:
  entity_id: media_player.samsung_frame_tv
```

**Note:** Art Mode shows artwork when TV is "off". To return to normal TV mode, press any button on remote.

---

## Sensors and Attributes

### `sensor.samsung_frame_art`

Main Frame Art sensor with current status and artwork information.

**State:** Number of available artworks

**Attributes:**
```yaml
current_content_id: MY_F0001      # Currently displayed artwork
matte_id: shadowbox_polar         # Current matte style
brightness: 50                     # Current brightness (0-100)
art_mode_status: on               # Art mode enabled/disabled
slideshow_status: off             # Slideshow active/inactive
```

---

### `sensor.samsung_frame_art_list`

List of all available artwork on the TV.

**State:** Number of artworks

**Attributes:**
```yaml
content_list:
  - content_id: MY_F0001
    category_id: MY-C0002
    file_name: photo_001.jpg
    image_date: "2024-01-15"
  
  - content_id: SAM-S2701
    category_id: MY-C0001
    file_name: Starry Night
    image_date: "2023-12-01"
```

**Category IDs:**
- `MY-C0001` - Art Store
- `MY-C0002` - Personal photos
- `MY-C0003` - Free content
- `MY-C0004` - Favorites

---

## Configuration Examples

### Create Directory Structure

Before using thumbnail services, create required directories:

```bash
mkdir -p /config/www/frame_art/personal
mkdir -p /config/www/frame_art/store
mkdir -p /config/www/frame_art/other
```

### Add to configuration.yaml

```yaml
# Enable Frame Art services (already included in integration)

# Optional: Track downloaded thumbnails
sensor:
  - platform: folder
    folder: /config/www/frame_art/personal
    filter: "*.jpg"
  
  - platform: folder
    folder: /config/www/frame_art/store
    filter: "*.jpg"
```

---

## Thumbnail Management

### Initial Setup

1. **Create directories:**
   ```bash
   mkdir -p /config/www/frame_art/{personal,store,other}
   ```

2. **Download all thumbnails:**
   ```yaml
   service: samsungtv_smart.art_get_thumbnails_batch
   data:
     entity_id: media_player.samsung_frame_tv
   ```

3. **Verify download:**
   ```bash
   ls -lh /config/www/frame_art/personal/
   ls -lh /config/www/frame_art/store/
   ```

### Daily Updates

Add automation to refresh thumbnails:

```yaml
automation:
  - alias: "Frame Art: Auto Update Thumbnails"
    trigger:
      - platform: time
        at: "03:00:00"
    condition:
      - condition: state
        entity_id: media_player.samsung_frame_tv
        state: "on"
    action:
      - service: samsungtv_smart.art_get_thumbnails_batch
        data:
          entity_id: media_player.samsung_frame_tv
          force_download: false  # Skip existing = fast!
```

---

## Automation Examples

### Morning Routine

```yaml
automation:
  - alias: "Frame Art: Morning Brightness"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: samsungtv_smart.art_set_brightness
        data:
          entity_id: media_player.samsung_frame_tv
          brightness: 80
      
      - service: samsungtv_smart.art_select_image
        data:
          entity_id: media_player.samsung_frame_tv
          content_id: MY_F0001  # Your morning photo
```

### Evening Routine

```yaml
automation:
  - alias: "Frame Art: Evening Dim"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      - service: samsungtv_smart.art_set_brightness
        data:
          entity_id: media_player.samsung_frame_tv
          brightness: 30
```

### Random Artwork on Motion

```yaml
automation:
  - alias: "Frame Art: Random on Motion"
    trigger:
      - platform: state
        entity_id: binary_sensor.living_room_motion
        to: "on"
    action:
      - service: samsungtv_smart.art_available
        data:
          entity_id: media_player.samsung_frame_tv
          category_id: MY-C0004  # Favorites
        response_variable: artwork_list
      
      - service: samsungtv_smart.art_select_image
        data:
          entity_id: media_player.samsung_frame_tv
          content_id: >
            {{ (artwork_list.artwork | random).content_id }}
```

### Brightness Based on Sun

```yaml
automation:
  - alias: "Frame Art: Adaptive Brightness"
    trigger:
      - platform: numeric_state
        entity_id: sun.sun
        attribute: elevation
    action:
      - service: samsungtv_smart.art_set_brightness
        data:
          entity_id: media_player.samsung_frame_tv
          brightness: >
            {% if state_attr('sun.sun', 'elevation') > 30 %}
              80
            {% elif state_attr('sun.sun', 'elevation') > 0 %}
              50
            {% else %}
              20
            {% endif %}
```

---

## Troubleshooting

### Thumbnails Not Downloading

**Symptoms:** Batch download fails or returns 0 bytes

**Solutions:**
1. Verify TV is on and in Art Mode
2. Check network connection
3. Restart TV (power cycle)
4. Try single thumbnail first:
   ```yaml
   service: samsungtv_smart.art_get_thumbnail
   data:
     entity_id: media_player.samsung_frame_tv
     content_id: MY_F0001
   ```

### Error Code -1 in Logs

**This is NORMAL!** Error code -1 indicates temporary connection issues.

The integration automatically retries (up to 3 times) and usually succeeds.

**Example log:**
```
ERROR: get_thumbnail error_code: -1 for SAM-S2701
DEBUG: Retrying SAM-S2701 (attempt 2/3)
INFO: Successfully downloaded SAM-S2701
```

**Action:** None required, automatic retry handles this.

### Large Entity Attributes

**Symptoms:** UI lag, large state file

**Cause:** Base64 thumbnail data in entity attributes (old versions)

**Solution:** Update to latest component version. New version removes base64 from attributes:
- Old: 2-3 MB per entity
- New: <10 KB per entity (99.5% reduction)

### Artwork Not Changing

**Possible causes:**
1. TV in regular mode (not Art Mode)
2. Invalid content_id
3. TV busy with other operation

**Solutions:**
```yaml
# Verify Art Mode enabled
service: samsungtv_smart.set_art_mode
target:
  entity_id: media_player.samsung_frame_tv

# Check available artworks
service: samsungtv_smart.art_available
data:
  entity_id: media_player.samsung_frame_tv

# Try different content_id
service: samsungtv_smart.art_select_image
data:
  entity_id: media_player.samsung_frame_tv
  content_id: MY_F0002
```

### Matte Changes Not Working

**Note:** Some TV models have limited matte support.

**Test available mattes:**
```yaml
# Try simple matte first
service: samsungtv_smart.art_change_matte
data:
  entity_id: media_player.samsung_frame_tv
  matte_id: none

# Then try with color
service: samsungtv_smart.art_change_matte
data:
  entity_id: media_player.samsung_frame_tv
  matte_id: shadowbox_black
```

---

## Advanced Features

### Custom Scripts

Create helper scripts in `scripts.yaml`:

```yaml
# Random favorite artwork
frame_art_random_favorite:
  alias: "Frame Art: Random Favorite"
  sequence:
    - service: samsungtv_smart.art_available
      data:
        entity_id: media_player.samsung_frame_tv
        category_id: MY-C0004
      response_variable: artwork_list
    
    - service: samsungtv_smart.art_select_image
      data:
        entity_id: media_player.samsung_frame_tv
        content_id: >
          {{ (artwork_list.artwork | random).content_id }}

# Apply matte from inputs
frame_art_apply_matte:
  alias: "Frame Art: Apply Matte"
  sequence:
    - service: samsungtv_smart.art_change_matte
      data:
        entity_id: media_player.samsung_frame_tv
        matte_id: >
          {% set type = states('input_select.frame_matte_type') %}
          {% set color = states('input_select.frame_matte_color') %}
          {% if type == 'none' %}
            none
          {% else %}
            {{ type ~ '_' ~ color }}
          {% endif %}
```

### Input Helpers

Add to `configuration.yaml`:

```yaml
input_number:
  frame_brightness:
    name: Frame TV Brightness
    min: 0
    max: 100
    step: 10
    initial: 50

input_select:
  frame_matte_type:
    name: Frame Type
    options:
      - none
      - shadowbox
      - modern
      - flexible

  frame_matte_color:
    name: Frame Color
    options:
      - black
      - white
      - polar
```

---

## See Also

- **[Frame Art Gallery Guide](Frame_Art_Gallery.md)** - Interactive Lovelace galleries
- **[Configuration Examples](../examples/frame_art/)** - Ready-to-use YAML files
- **[Main README](../README.md)** - Integration overview

---

**Need more help?** 
- 🐛 [Report issues](https://github.com/ollo69/ha-samsungtv-smart/issues)
- 💬 [Community forum](https://community.home-assistant.io/)

---

Enjoy your Frame Art! 🎨✨
