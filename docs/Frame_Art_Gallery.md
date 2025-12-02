# 🖼️ Frame Art Gallery - Lovelace Guide

Create interactive artwork galleries in Home Assistant with click-to-display functionality.

---

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Gallery Types](#gallery-types)
- [Advanced Layouts](#advanced-layouts)
- [Template Sensors](#template-sensors)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)

---

## Overview

Frame Art Gallery transforms your Home Assistant dashboard into an interactive art gallery:

- 📸 Click thumbnails to display artwork on Frame TV
- 🎨 Separate galleries for personal photos, favorites, and Art Store
- 🔄 Auto-generated from actual TV content
- 📱 Fully responsive layouts
- ⚡ Fast loading with cached thumbnails

![Gallery Example](https://i.imgur.com/example.png)

---

## Requirements

### Required Components

1. **SamsungTV Smart integration** with Frame Art support

2. **Gallery Card** (choose one):

   **Option A: folder-gallery-card** ⭐ **RECOMMENDED**
   - Included in this integration (see `www/community/folder-gallery-card/`)
   - Faster and cleaner than auto-entities
   - Better performance with large galleries
   - Simpler configuration
   - Installation: [See folder-gallery-card README](../../www/community/folder-gallery-card/README.md)

   **Option B: auto-entities**
   - Install via HACS: Search "auto-entities"
   - Or manually: [GitHub](https://github.com/thomasloven/lovelace-auto-entities)
   - More flexible but more complex

3. **Downloaded thumbnails** (see [Quick Start](#quick-start))

### Optional But Recommended

- **card-mod** for custom styling
- **Browser Mod** for popups/modals

---

## Quick Start

### Step 1: Install Prerequisites

```bash
# Install auto-entities via HACS
# Or add to configuration.yaml:
lovelace:
  resources:
    - url: /hacsfiles/lovelace-auto-entities/auto-entities.js
      type: module
```

### Step 2: Create Directory Structure

```bash
mkdir -p /config/www/frame_art/personal
mkdir -p /config/www/frame_art/store
mkdir -p /config/www/frame_art/other
```

### Step 3: Download Thumbnails

```yaml
service: samsungtv_smart.art_get_thumbnails_batch
data:
  entity_id: media_player.samsung_frame_tv
```

**First run:** 2-5 minutes  
**Subsequent runs:** 2-5 seconds (skips existing)

### Step 4: Add Template Sensors

Add to `configuration.yaml`:

```yaml
template:
  - sensor:
      - name: "Frame Art Personal Gallery"
        unique_id: frame_art_personal_gallery
        state: >
          {% set list = state_attr('sensor.samsung_frame_art_list', 'content_list') or [] %}
          {% set personal = list | selectattr('category_id', 'eq', 'MY-C0002') | list %}
          {{ personal | length }}
        attributes:
          images: >
            {% set ns = namespace(images=[]) %}
            {% for item in state_attr('sensor.samsung_frame_art_list', 'content_list') or [] %}
              {% if item.category_id == 'MY-C0002' %}
                {% set ns.images = ns.images + [{
                  'path': '/local/frame_art/personal/' ~ item.content_id ~ '.jpg',
                  'content_id': item.content_id
                }] %}
              {% endif %}
            {% endfor %}
            {{ ns.images }}
```

### Step 5: Create Gallery Dashboard

Add to Lovelace (example in [Gallery Types](#gallery-types) section).

---

## Gallery Types

### Personal Photos Gallery

Interactive grid of your personal photos.

```yaml
type: custom:auto-entities
card:
  type: grid
  columns: 4
  square: true
  title: 📷 My Photos
filter:
  template: |
    {% for img in state_attr('sensor.frame_art_personal_gallery', 'images') or [] %}
      {{
        {
          'type': 'picture',
          'image': img.path,
          'tap_action': {
            'action': 'call-service',
            'service': 'samsungtv_smart.art_select_image',
            'service_data': {
              'entity_id': 'media_player.samsung_frame_tv',
              'content_id': img.content_id,
              'show': true
            }
          },
          'hold_action': {
            'action': 'more-info'
          }
        }
      }},
    {% endfor %}
show_empty: true
card_param: cards
```

**Features:**
- 4-column grid layout
- Square thumbnails
- Click to display on TV
- Hold for more info

---

### Art Store Gallery

Samsung Art Store purchased images.

**Template Sensor:**

```yaml
template:
  - sensor:
      - name: "Frame Art Store Gallery"
        unique_id: frame_art_store_gallery
        state: >
          {% set list = state_attr('sensor.samsung_frame_art_list', 'content_list') or [] %}
          {% set store = list | selectattr('content_id', 'match', '^SAM-') | list %}
          {{ store | length }}
        attributes:
          images: >
            {% set ns = namespace(images=[]) %}
            {% for item in state_attr('sensor.samsung_frame_art_list', 'content_list') or [] %}
              {% if item.content_id.startswith('SAM-') %}
                {% set ns.images = ns.images + [{
                  'path': '/local/frame_art/store/' ~ item.content_id ~ '.jpg',
                  'content_id': item.content_id
                }] %}
              {% endif %}
            {% endfor %}
            {{ ns.images }}
```

**Lovelace Card:**

```yaml
type: custom:auto-entities
card:
  type: grid
  columns: 4
  square: true
  title: 🎨 Art Store
filter:
  template: |
    {% for img in state_attr('sensor.frame_art_store_gallery', 'images') or [] %}
      {{
        {
          'type': 'picture',
          'image': img.path,
          'tap_action': {
            'action': 'call-service',
            'service': 'samsungtv_smart.art_select_image',
            'service_data': {
              'entity_id': 'media_player.samsung_frame_tv',
              'content_id': img.content_id,
              'show': true
            }
          }
        }
      }},
    {% endfor %}
show_empty: true
card_param: cards
```

---

### Favorites Gallery

Quick access to favorite artwork.

**Template Sensor:**

```yaml
template:
  - sensor:
      - name: "Frame Art Favorites Gallery"
        unique_id: frame_art_favorites_gallery
        state: >
          {% set list = state_attr('sensor.samsung_frame_art_list', 'content_list') or [] %}
          {% set favorites = list | selectattr('category_id', 'eq', 'MY-C0004') | list %}
          {{ favorites | length }}
        attributes:
          images: >
            {% set ns = namespace(images=[]) %}
            {% for item in state_attr('sensor.samsung_frame_art_list', 'content_list') or [] %}
              {% if item.category_id == 'MY-C0004' %}
                {% set subdir = 'personal' if item.content_id.startswith('MY_F') else ('store' if item.content_id.startswith('SAM-') else 'other') %}
                {% set ns.images = ns.images + [{
                  'path': '/local/frame_art/' ~ subdir ~ '/' ~ item.content_id ~ '.jpg',
                  'content_id': item.content_id
                }] %}
              {% endif %}
            {% endfor %}
            {{ ns.images }}
```

**Lovelace Card:**

```yaml
type: custom:auto-entities
card:
  type: grid
  columns: 4
  square: true
  title: ⭐ Favorites
filter:
  template: |
    {% for img in state_attr('sensor.frame_art_favorites_gallery', 'images') or [] %}
      {{
        {
          'type': 'picture',
          'image': img.path,
          'tap_action': {
            'action': 'call-service',
            'service': 'samsungtv_smart.art_select_image',
            'service_data': {
              'entity_id': 'media_player.samsung_frame_tv',
              'content_id': img.content_id,
              'show': true
            }
          }
        }
      }},
    {% endfor %}
show_empty: true
card_param: cards
```

---

## Advanced Layouts

### Compact Gallery (3 Columns)

Better for smaller screens:

```yaml
type: custom:auto-entities
card:
  type: grid
  columns: 3
  square: true
  title: 📷 Compact View
filter:
  template: |
    {% for img in state_attr('sensor.frame_art_personal_gallery', 'images') or [] %}
      {{
        {
          'type': 'picture',
          'image': img.path,
          'tap_action': {
            'action': 'call-service',
            'service': 'samsungtv_smart.art_select_image',
            'service_data': {
              'entity_id': 'media_player.samsung_frame_tv',
              'content_id': img.content_id,
              'show': true
            }
          }
        }
      }},
    {% endfor %}
```

---

### Large Thumbnails (2 Columns)

For detailed viewing:

```yaml
type: custom:auto-entities
card:
  type: grid
  columns: 2
  square: true
  title: 🖼️ Large View
filter:
  template: |
    {% for img in state_attr('sensor.frame_art_favorites_gallery', 'images') or [] %}
      {{
        {
          'type': 'picture',
          'image': img.path,
          'tap_action': {
            'action': 'call-service',
            'service': 'samsungtv_smart.art_select_image',
            'service_data': {
              'entity_id': 'media_player.samsung_frame_tv',
              'content_id': img.content_id,
              'show': true
            }
          }
        }
      }},
    {% endfor %}
```

---

### Mobile-Optimized Layout

Responsive for phones/tablets:

```yaml
type: vertical-stack
cards:
  # Quick brightness controls
  - type: horizontal-stack
    cards:
      - type: button
        name: Bright
        icon: mdi:brightness-7
        tap_action:
          action: call-service
          service: input_number.set_value
          service_data:
            entity_id: input_number.frame_brightness
            value: 80
      
      - type: button
        name: Dim
        icon: mdi:brightness-4
        tap_action:
          action: call-service
          service: input_number.set_value
          service_data:
            entity_id: input_number.frame_brightness
            value: 30
  
  # 2-column gallery for mobile
  - type: custom:auto-entities
    card:
      type: grid
      columns: 2
      square: true
    filter:
      template: |
        {% for img in state_attr('sensor.frame_art_favorites_gallery', 'images') or [] %}
          {{
            {
              'type': 'picture',
              'image': img.path,
              'tap_action': {
                'action': 'call-service',
                'service': 'samsungtv_smart.art_select_image',
                'service_data': {
                  'entity_id': 'media_player.samsung_frame_tv',
                  'content_id': img.content_id,
                  'show': true
                }
              }
            }
          }},
        {% endfor %}
```

---

### List View with Details

Shows content IDs and metadata:

```yaml
type: custom:auto-entities
card:
  type: entities
  title: 📋 Artwork List
filter:
  template: |
    {% for img in state_attr('sensor.frame_art_personal_gallery', 'images') or [] %}
      {{
        {
          'type': 'button',
          'name': img.content_id,
          'icon': 'mdi:image',
          'tap_action': {
            'action': 'call-service',
            'service': 'samsungtv_smart.art_select_image',
            'service_data': {
              'entity_id': 'media_player.samsung_frame_tv',
              'content_id': img.content_id,
              'show': true
            }
          }
        }
      }},
    {% endfor %}
```

---

## Template Sensors

### Complete Configuration

Add all three gallery sensors to `configuration.yaml`:

```yaml
template:
  - sensor:
      # Personal Photos
      - name: "Frame Art Personal Gallery"
        unique_id: frame_art_personal_gallery
        state: >
          {% set list = state_attr('sensor.samsung_frame_art_list', 'content_list') or [] %}
          {% set personal = list | selectattr('category_id', 'eq', 'MY-C0002') | list %}
          {{ personal | length }}
        attributes:
          images: >
            {% set ns = namespace(images=[]) %}
            {% for item in state_attr('sensor.samsung_frame_art_list', 'content_list') or [] %}
              {% if item.category_id == 'MY-C0002' %}
                {% set ns.images = ns.images + [{
                  'path': '/local/frame_art/personal/' ~ item.content_id ~ '.jpg',
                  'filename': item.content_id ~ '.jpg',
                  'name': item.content_id,
                  'content_id': item.content_id
                }] %}
              {% endif %}
            {% endfor %}
            {{ ns.images }}

      # Art Store
      - name: "Frame Art Store Gallery"
        unique_id: frame_art_store_gallery
        state: >
          {% set list = state_attr('sensor.samsung_frame_art_list', 'content_list') or [] %}
          {% set store = list | selectattr('content_id', 'match', '^SAM-') | list %}
          {{ store | length }}
        attributes:
          images: >
            {% set ns = namespace(images=[]) %}
            {% for item in state_attr('sensor.samsung_frame_art_list', 'content_list') or [] %}
              {% if item.content_id.startswith('SAM-') %}
                {% set ns.images = ns.images + [{
                  'path': '/local/frame_art/store/' ~ item.content_id ~ '.jpg',
                  'filename': item.content_id ~ '.jpg',
                  'name': item.content_id,
                  'content_id': item.content_id
                }] %}
              {% endif %}
            {% endfor %}
            {{ ns.images }}
      
      # Favorites
      - name: "Frame Art Favorites Gallery"
        unique_id: frame_art_favorites_gallery
        state: >
          {% set list = state_attr('sensor.samsung_frame_art_list', 'content_list') or [] %}
          {% set favorites = list | selectattr('category_id', 'eq', 'MY-C0004') | list %}
          {{ favorites | length }}
        attributes:
          images: >
            {% set ns = namespace(images=[]) %}
            {% for item in state_attr('sensor.samsung_frame_art_list', 'content_list') or [] %}
              {% if item.category_id == 'MY-C0004' %}
                {% set subdir = 'personal' if item.content_id.startswith('MY_F') else ('store' if item.content_id.startswith('SAM-') else 'other') %}
                {% set ns.images = ns.images + [{
                  'path': '/local/frame_art/' ~ subdir ~ '/' ~ item.content_id ~ '.jpg',
                  'filename': item.content_id ~ '.jpg',
                  'name': item.content_id,
                  'content_id': item.content_id,
                  'subdirectory': subdir
                }] %}
              {% endif %}
            {% endfor %}
            {{ ns.images }}
```

---

## Customization

### Custom Grid Sizes

Adjust `columns` value for different layouts:

```yaml
columns: 2  # 2-column layout (large thumbnails)
columns: 3  # 3-column layout (medium)
columns: 4  # 4-column layout (default)
columns: 5  # 5-column layout (compact)
columns: 6  # 6-column layout (very compact)
```

### Non-Square Thumbnails

```yaml
card:
  type: grid
  columns: 4
  square: false  # Allow rectangular thumbnails
```

### Custom Tap Actions

#### Open in New Tab

```yaml
tap_action:
  action: url
  url_path: !secret frame_tv_url
```

#### Show Confirmation

```yaml
tap_action:
  confirmation:
    text: Display this artwork?
  action: call-service
  service: samsungtv_smart.art_select_image
  service_data:
    entity_id: media_player.samsung_frame_tv
    content_id: img.content_id
```

#### Multiple Actions

```yaml
tap_action:
  action: call-service
  service: samsungtv_smart.art_select_image
  service_data:
    entity_id: media_player.samsung_frame_tv
    content_id: img.content_id

hold_action:
  action: call-service
  service: persistent_notification.create
  service_data:
    message: "Displaying {{ img.content_id }}"
```

### Card Styling with card-mod

```yaml
type: custom:auto-entities
card:
  type: grid
  columns: 4
  square: true
  card_mod:
    style: |
      ha-card {
        border: 2px solid var(--primary-color);
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
      }
filter:
  template: |
    {% for img in state_attr('sensor.frame_art_personal_gallery', 'images') or [] %}
      {{
        {
          'type': 'picture',
          'image': img.path,
          'card_mod': {
            'style': '''
              ha-card {
                border-radius: 8px;
                transition: transform 0.2s;
              }
              ha-card:hover {
                transform: scale(1.05);
                box-shadow: 0 8px 16px rgba(0,0,0,0.3);
              }
            '''
          },
          'tap_action': {
            'action': 'call-service',
            'service': 'samsungtv_smart.art_select_image',
            'service_data': {
              'entity_id': 'media_player.samsung_frame_tv',
              'content_id': img.content_id
            }
          }
        }
      }},
    {% endfor %}
```

---

## Troubleshooting

### Gallery Shows "No entities"

**Causes:**
1. Template sensors not created
2. Thumbnails not downloaded
3. Sensor has no `images` attribute

**Solutions:**

```yaml
# Check if template sensors exist
# Developer Tools > States
# Search for: sensor.frame_art_personal_gallery

# Check sensor attributes
# Should have 'images' list with paths

# Verify thumbnails downloaded
ls /config/www/frame_art/personal/

# Re-download thumbnails
service: samsungtv_smart.art_get_thumbnails_batch
data:
  entity_id: media_player.samsung_frame_tv
```

### Thumbnails Not Loading

**Causes:**
1. Wrong file paths
2. Files don't exist
3. Permission issues

**Solutions:**

```bash
# Check files exist
ls -lh /config/www/frame_art/personal/
ls -lh /config/www/frame_art/store/

# Check permissions
chmod -R 755 /config/www/frame_art/

# Verify URLs in browser
http://YOUR_HA_IP:8123/local/frame_art/personal/MY_F0001.jpg
```

### Click Not Working

**Causes:**
1. TV off or not in Art Mode
2. Invalid content_id
3. Network issue

**Solutions:**

```yaml
# Enable Art Mode first
service: samsungtv_smart.set_art_mode
target:
  entity_id: media_player.samsung_frame_tv

# Verify content_id exists
# Check sensor.samsung_frame_art_list attributes

# Test with Developer Tools
service: samsungtv_smart.art_select_image
data:
  entity_id: media_player.samsung_frame_tv
  content_id: MY_F0001
```

### Gallery Not Updating

**Issue:** New photos don't appear

**Solutions:**

```yaml
# Refresh artwork list
service: samsungtv_smart.art_available
data:
  entity_id: media_player.samsung_frame_tv

# Download new thumbnails
service: samsungtv_smart.art_get_thumbnails_batch
data:
  entity_id: media_player.samsung_frame_tv

# Restart Home Assistant
# Settings > System > Restart
```

---

## Performance Tips

### Optimize Thumbnail Size

Thumbnails are automatically resized by the TV API, but you can optimize further:

```bash
# Install ImageMagick
apt-get install imagemagick

# Batch resize thumbnails
cd /config/www/frame_art/personal
mogrify -resize 400x400 -quality 85 *.jpg
```

### Lazy Loading

For large galleries (100+ images), consider pagination:

```yaml
type: custom:auto-entities
card:
  type: grid
  columns: 4
  square: true
  title: 📷 My Photos (Page 1)
filter:
  template: |
    {% set images = state_attr('sensor.frame_art_personal_gallery', 'images') or [] %}
    {% for img in images[:20] %}  {# First 20 images #}
      {{
        {
          'type': 'picture',
          'image': img.path,
          'tap_action': {
            'action': 'call-service',
            'service': 'samsungtv_smart.art_select_image',
            'service_data': {
              'entity_id': 'media_player.samsung_frame_tv',
              'content_id': img.content_id
            }
          }
        }
      }},
    {% endfor %}
```

---

## Complete Dashboard Example

See [examples/frame_art/lovelace.yaml](../examples/frame_art/lovelace.yaml) for a full working dashboard including:

- Control panel
- Multiple gallery views
- Brightness/matte controls
- Quick action buttons
- Mobile-optimized layout

---

## See Also

- **[Frame Art Guide](Frame_Art.md)** - Complete service documentation
- **[Configuration Examples](../examples/frame_art/)** - Ready-to-use YAML files
- **[Main README](../README.md)** - Integration overview

---

**Need help?**
- 🐛 [Report issues](https://github.com/ollo69/ha-samsungtv-smart/issues)
- 💬 [Community forum](https://community.home-assistant.io/)

---

Happy gallery building! 🖼️✨
