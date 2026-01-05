**This is a fork of ha-samsungtv-smart by @fjwillemsen with fixes by @chansearrington.**

# Samsung TV Smart - Frame Art Edition

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/fjwillemsen/ha-samsungtv-smart.svg)](https://github.com/fjwillemsen/ha-samsungtv-smart/releases)

📺 Home Assistant integration for Samsung Smart TVs with **enhanced Frame TV Art Mode support** and **OAuth2 authentication**.

This is a fork of [ollo69/ha-samsungtv-smart](https://github.com/ollo69/ha-samsungtv-smart) with significant improvements for Samsung Frame TV users.

---

## ✨ What's New in This Fork

### 🔐 OAuth2 Authentication (No More PAT Expiration!)

The original integration uses Personal Access Tokens (PAT) that expire after a few months, requiring manual renewal. This fork implements **full OAuth2 authentication** with:

- **Automatic token refresh** - Tokens are refreshed 5 minutes before expiration
- **Race condition protection** - Global lock prevents concurrent refresh attempts
- **24-hour token validity** - SmartThings OAuth tokens last 24 hours with automatic renewal
- **No more manual PAT renewal** - Set it and forget it!

### 🖼️ Enhanced Frame TV Art Mode

Complete control over your Samsung Frame TV's Art Mode:

- **Art Mode Switch** - Dedicated switch entity with retry logic
- **Frame Art Sensor** - Real-time artwork tracking with thumbnail support
- **Slideshow Automation** - Configure automatic artwork rotation
- **Matte Control** - Change frame styles and colors
- **Thumbnail Management** - Download and cache artwork thumbnails locally
- **Orphan Cleanup** - Automatically remove thumbnails for deleted favorites

### 🔧 Technical Improvements

- **WebSocket Auto-Reconnection** - Automatically reconnects when TV closes connection
- **pysmartthings v6.0+ Compatibility** - Updated for latest SmartThings library
- **Improved Error Handling** - Better logging and retry mechanisms
- **SmartThings Illuminance Sensor** - Ambient light sensor support
- **Brightness Intensity Sensor** - Art Mode brightness tracking

---

## 📋 Requirements

- Samsung Smart TV (2016+ models)
- Samsung Frame TV (for Art Mode features)
- Home Assistant 2024.1.0 or newer
- SmartThings account linked to your TV
- **For OAuth2**: SmartThings Developer Account (free)

---

## 🚀 Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the three dots menu → **Custom repositories**
4. Add: `https://github.com/fjwillemsen/ha-samsungtv-smart`
5. Category: **Integration**
6. Click **Add**
7. Search for "Samsung TV Smart" and install
8. Restart Home Assistant

### Manual Installation

1. Download the latest release from GitHub
2. Copy the `samsungtv_smart` folder to `/config/custom_components/`
3. Restart Home Assistant

---

## 🔐 OAuth2 Setup (Recommended)

OAuth2 provides automatic token refresh, eliminating the need for manual PAT renewal.

### Step 1: Create SmartThings OAuth Application

1. Go to [SmartThings Developer Workspace](https://smartthings.developer.samsung.com/workspace)
2. Sign in with your Samsung account
3. Click **New Project** → **Device Integration** → **SmartThings Cloud Connector**
4. Name your project (e.g., "Home Assistant Integration")
5. Go to **Develop** → **Registration** → **App Registration**
6. Click **Create New**

### Step 2: Configure OAuth Settings

In the App Registration form:

| Field | Value |
|-------|-------|
| **App Name** | Home Assistant Samsung TV |
| **App Type** | Automation App |
| **OAuth Scope** | `r:devices:*` and `x:devices:*` |
| **Redirect URI** | `https://my.home-assistant.io/redirect/oauth` |

7. Click **Save** and note your:
   - **Client ID** (OAuth Client Id)
   - **Client Secret** (OAuth Client Secret)

> ⚠️ **Important**: Use the "OAuth Client Id", NOT the "App Id"!

### Step 3: Configure Home Assistant

Add your credentials to Home Assistant:

**Option A: Via UI**
1. Go to **Settings** → **Devices & Services** → **Application Credentials**
2. Click **Add Credentials**
3. Select **Samsung TV Smart**
4. Enter your Client ID and Client Secret

**Option B: Via configuration.yaml**
```yaml
# configuration.yaml
application_credentials:
  - platform: samsungtv_smart
    client_id: "YOUR_CLIENT_ID"
    client_secret: "YOUR_CLIENT_SECRET"
```

### Step 4: Add Integration with OAuth

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration** → **Samsung TV Smart**
3. Select **SmartThings OAuth** as authentication method
4. Complete the OAuth flow in your browser
5. Your TV should now appear with OAuth authentication

---

## 🖼️ Frame TV Art Mode Features

### Entities Created

| Entity | Type | Description |
|--------|------|-------------|
| `media_player.samsung_*` | Media Player | Main TV control with art mode attributes |
| `switch.samsung_*_frame_art_mode` | Switch | Toggle Art Mode on/off |
| `sensor.samsung_*_frame_art` | Sensor | Current artwork info and thumbnail |
| `sensor.samsung_*_illuminance` | Sensor | Ambient light level |
| `sensor.samsung_*_brightness_intensity` | Sensor | Art Mode brightness |

### Available Services

#### Basic Art Mode Control

```yaml
# Get Art Mode status
service: samsungtv_smart.art_get_artmode
target:
  entity_id: media_player.samsung_frame

# Turn Art Mode on/off
service: samsungtv_smart.art_set_artmode
target:
  entity_id: media_player.samsung_frame
data:
  enabled: true
```

#### Artwork Selection

```yaml
# Select specific artwork
service: samsungtv_smart.art_select_image
target:
  entity_id: media_player.samsung_frame
data:
  content_id: "SAM-S1234567"
  
# Get available artworks
service: samsungtv_smart.art_available
target:
  entity_id: media_player.samsung_frame
data:
  category_id: "MY-C0004"  # Optional: filter by category
```

#### Matte (Frame) Control

```yaml
# Change matte style and color
service: samsungtv_smart.art_change_matte
target:
  entity_id: media_player.samsung_frame
data:
  matte_type: "shadowbox"
  matte_color: "neutral"

# Available matte types:
# none, modernthin, modern, modernwide, flexible, shadowbox, panoramic, triptych, mix, squares

# Available colors (varies by matte type):
# neutral, antique, warm, polar, sand, seafoam, sage, burgandy, navy, apricot, byzantine, lavender, redorange, ink, peach
```

#### Slideshow & Auto-Rotation

```yaml
# Configure slideshow
service: samsungtv_smart.art_set_slideshow
target:
  entity_id: media_player.samsung_frame
data:
  duration: "15min"  # 1min, 5min, 10min, 15min, 30min, 1hour, 2hour, 4hour, 8hour
  shuffle: true
  category_id: 4  # 2=Personal, 4=Favorites

# Configure auto-rotation (similar to slideshow)
service: samsungtv_smart.art_set_auto_rotation
target:
  entity_id: media_player.samsung_frame
data:
  duration: "1hour"
  shuffle: true
  category_id: 4
```

#### Brightness Control

```yaml
# Set Art Mode brightness (0-100)
service: samsungtv_smart.art_set_brightness
target:
  entity_id: media_player.samsung_frame
data:
  brightness: 50

# Get current brightness
service: samsungtv_smart.art_get_brightness
target:
  entity_id: media_player.samsung_frame
```

#### Thumbnail Management

```yaml
# Download single thumbnail
service: samsungtv_smart.art_get_thumbnail
target:
  entity_id: media_player.samsung_frame
data:
  content_id: "SAM-S1234567"
  save_to_file: true

# Batch download with orphan cleanup
service: samsungtv_smart.art_get_thumbnails_batch
target:
  entity_id: media_player.samsung_frame
data:
  favorites_only: true
  cleanup_orphans: true  # Remove thumbnails for deleted favorites
  force_download: false  # Skip existing files
```

#### Favorites Management

```yaml
# Add/remove from favorites
service: samsungtv_smart.art_set_favourite
target:
  entity_id: media_player.samsung_frame
data:
  content_id: "SAM-S1234567"
  favourite: true
```

---

## 📂 Thumbnail Storage

Thumbnails are saved to organized directories:

```
/config/www/frame_art/
├── current.jpg          # Currently displayed artwork
├── personal/            # User-uploaded images (MY_F*)
│   ├── MY_F0001.jpg
│   └── MY_F0002.jpg
├── store/               # Samsung Art Store (SAM-S*)
│   ├── SAM-S1234567.jpg
│   └── SAM-S7654321.jpg
└── other/               # Other content types
```

Access thumbnails via:
- Current: `/local/frame_art/current.jpg`
- Store: `/local/frame_art/store/SAM-S1234567.jpg`
- Personal: `/local/frame_art/personal/MY_F0001.jpg`

---

## 🤖 Automation Examples

### Weekend Art Slideshow

```yaml
alias: "Frame Art: Weekend Slideshow"
triggers:
  - trigger: time
    at: "09:00:00"
conditions:
  - condition: time
    weekday:
      - sat
      - sun
actions:
  - action: samsungtv_smart.art_set_slideshow
    target:
      entity_id: media_player.samsung_frame
    data:
      duration: "15min"
      shuffle: true
      category_id: 4
mode: single
```

### Sync Favorites Thumbnails

```yaml
alias: "Frame Art: Sync Favorites"
triggers:
  - trigger: time_pattern
    hours: "/6"  # Every 6 hours
actions:
  - action: samsungtv_smart.art_get_thumbnails_batch
    target:
      entity_id: media_player.samsung_frame
    data:
      favorites_only: true
      cleanup_orphans: true
  - delay:
      seconds: 2
  - action: homeassistant.update_entity
    target:
      entity_id: sensor.store  # Folder sensor for gallery card
mode: single
```

### Sync Matte Selection from TV

When matte is changed on the TV, update input_select helpers:

```yaml
alias: "Frame Art: Sync Matte from TV"
triggers:
  - trigger: state
    entity_id: sensor.samsung_frame_frame_art
    attribute: current_matte_id
actions:
  - variables:
      matte_id: >-
        {{ state_attr('sensor.samsung_frame_frame_art', 'current_matte_id') |
        default('none', true) | lower }}
      matte_type: |
        {% if matte_id in ['none', '', None] or '_' not in matte_id %}
          none
        {% else %}
          {{ matte_id.split('_')[0] | lower }}
        {% endif %}
      matte_color: |
        {% if matte_id in ['none', '', None] or '_' not in matte_id %}
          {{ states('input_select.frame_matte_color') }}
        {% else %}
          {{ matte_id.split('_')[1] | lower }}
        {% endif %}
  - action: input_select.select_option
    target:
      entity_id: input_select.frame_matte_type
    data:
      option: "{{ matte_type | trim }}"
  - action: input_select.select_option
    target:
      entity_id: input_select.frame_matte_color
    data:
      option: "{{ matte_color | trim }}"
mode: queued
```

### Art Mode at Night

```yaml
alias: "Frame Art: Night Mode"
triggers:
  - trigger: time
    at: "22:00:00"
conditions:
  - condition: state
    entity_id: media_player.samsung_frame
    state: "on"
actions:
  - action: switch.turn_on
    target:
      entity_id: switch.samsung_frame_frame_art_mode
  - action: samsungtv_smart.art_set_brightness
    target:
      entity_id: media_player.samsung_frame
    data:
      brightness: 20
mode: single
```

---

## 🖼️ Custom Folder Gallery Card

Display your Frame TV artwork collection in a Lovelace gallery.

### Installation

1. Copy `folder-gallery-card.js` to `/config/www/community/folder-gallery-card/`
2. Add to Lovelace resources:
   ```yaml
   resources:
     - url: /local/community/folder-gallery-card/folder-gallery-card.js
       type: module
   ```

### Configuration

1. First, create a folder sensor to monitor your thumbnails:

```yaml
# configuration.yaml
sensor:
  - platform: folder
    folder: /config/www/frame_art/store
    filter: "*.jpg"
    scan_interval: 30
```

2. Add the card to your dashboard:

```yaml
type: custom:folder-gallery-card
title: Frame TV Favorites
folder_sensor: sensor.store
folder: /local/frame_art/store
columns: 4
image_height: 160px
aspect_ratio: "1"
tap_action: lightbox
hold_action:
  service: samsungtv_smart.art_select_image
  target:
    entity_id: media_player.samsung_frame
  data:
    content_id: "{{content_id}}"
```

### Card Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `title` | string | - | Card title |
| `folder_sensor` | string | - | Folder sensor entity ID |
| `folder` | string | - | Base folder path (e.g., `/local/frame_art/store`) |
| `columns` | number | 4 | Number of columns |
| `image_height` | string | `150px` | Image height |
| `aspect_ratio` | string | - | Aspect ratio (e.g., "1" for square, "16/9") |
| `gap` | string | `8px` | Gap between images |
| `border_radius` | string | `8px` | Image border radius |
| `tap_action` | string | - | Action on tap: `lightbox`, `action`, `more-info` |
| `hold_action` | object | - | Service call on hold |

### Template Variables

Use these in your action data:
- `{{content_id}}` - Artwork content ID (extracted from filename)
- `{{filename}}` - Full filename
- `{{image_path}}` - Full image path
- `{{name}}` - Artwork name

---

## 🐛 Troubleshooting

### OAuth Token Refresh Issues

If you see "Invalid refresh token" errors:

1. Check that only one instance is refreshing tokens (global lock should prevent this)
2. Verify your Client ID and Secret are correct
3. Try reconfiguring the integration with OAuth

### Art Mode Commands Fail

If Art Mode commands fail silently:

1. Enable debug logging:
   ```yaml
   logger:
     logs:
       custom_components.samsungtv_smart: debug
       custom_components.samsungtv_smart.api.art: debug
   ```

2. Check for WebSocket disconnection in logs
3. The integration now auto-reconnects, but a restart may help

### Thumbnails Not Downloading

1. Ensure TV is in Art Mode or on
2. Check if content is DRM-protected (Samsung Art Store items may have restrictions)
3. Look for timeout errors in logs

### Gallery Card Not Updating

After removing favorites:
1. Call `art_get_thumbnails_batch` with `cleanup_orphans: true`
2. Wait 2 seconds
3. Call `homeassistant.update_entity` on your folder sensor

---

## 🔧 Debug Logging

```yaml
# configuration.yaml
logger:
  default: warning
  logs:
    custom_components.samsungtv_smart: debug
    custom_components.samsungtv_smart.api.art: debug
    custom_components.samsungtv_smart.api.smartthings: debug
    custom_components.samsungtv_smart.switch: debug
    custom_components.samsungtv_smart.sensor: debug
```

---

## 📝 Changelog

### v0.9.0 (Frame Art Edition)

#### OAuth2 Authentication
- ✨ Full OAuth2 support with automatic token refresh
- ✨ Global lock prevents race conditions during token refresh
- ✨ Token propagation via callback to all components
- ✨ Fallback mechanism for legacy PAT authentication

#### Frame TV Art Mode
- ✨ New `switch.samsung_*_frame_art_mode` entity with retry logic
- ✨ New `sensor.samsung_*_frame_art` with artwork tracking
- ✨ Thumbnail download and caching to local storage
- ✨ Batch thumbnail download with `cleanup_orphans` option
- ✨ Slideshow and auto-rotation configuration
- ✨ Matte (frame) style and color control
- ✨ Photo filter support
- ✨ Brightness control (0-100 scale)

#### Technical Improvements
- 🔧 WebSocket auto-reconnection when TV closes connection
- 🔧 pysmartthings v6.0+ compatibility (Capability.switch → string constants)
- 🔧 SmartThings illuminance sensor support
- 🔧 Brightness intensity sensor
- 🔧 Improved error handling and logging
- 🔧 Exponential backoff for failed operations

---

## 🙏 Credits

- [ollo69](https://github.com/ollo69) - Original ha-samsungtv-smart integration
- [NickWaterton](https://github.com/NickWaterton) - samsung-tv-ws-api reference
- Samsung SmartThings - API documentation

---

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
