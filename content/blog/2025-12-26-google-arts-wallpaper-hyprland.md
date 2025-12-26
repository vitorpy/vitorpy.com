---
date: "2025-12-26T00:00:00Z"
tags:
  - linux
  - hyprland
  - systemd
  - automation
title: Daily Art Wallpapers with Google Arts & Culture and Systemd
---

Google has a lovely [Arts & Culture extension](https://chromewebstore.google.com/detail/google-arts-culture/akimgimeeoiognljlfchpbkpfbmeapkh) for Chrome that displays a random masterpiece from museums around the world every time you open a new tab. It's a nice way to discover art you'd never otherwise encounter.

The problem: it only works when Chrome is open. I wanted this on my desktop wallpaper, system-wide, updating automatically even if I never touch a browser.

Here's my setup on Arch Linux with Hyprland.

![Desktop with Google Arts & Culture wallpaper](/images/google-arts-wallpaper.png)

## How It Works

Google's extension pulls artwork from a public JSON endpoint that lists featured pieces with high-resolution image URLs. A simple bash script fetches this list, picks a random artwork, downloads it, and uses `hyprctl` to set it as the wallpaper.

The script also saves metadata about the current artwork, so you can always find out what's on your screen and visit the museum page.

## The Script

Save this to `~/.local/bin/google-arts-wallpaper`:

```bash
#!/bin/bash
# Google Arts & Culture Wallpaper Fetcher

set -euo pipefail

DATA_DIR="${HOME}/.local/share/google-arts"
API_URL="https://www.gstatic.com/culturalinstitute/tabext/imax_2_2.json"
RESOLUTION="2560"
CURRENT_IMAGE="${DATA_DIR}/current.webp"
CURRENT_META="${DATA_DIR}/current.json"

mkdir -p "${DATA_DIR}"

# Fetch artwork list and pick a random one
ARTWORK=$(curl -sS "${API_URL}" | jq -c '.[]' | shuf -n 1)

if [[ -z "${ARTWORK}" ]]; then
    echo "Error: Failed to fetch artwork data" >&2
    exit 1
fi

# Extract metadata
TITLE=$(echo "${ARTWORK}" | jq -r '.title')
CREATOR=$(echo "${ARTWORK}" | jq -r '.creator')
ATTRIBUTION=$(echo "${ARTWORK}" | jq -r '.attribution')
IMAGE_BASE=$(echo "${ARTWORK}" | jq -r '.image')
LINK=$(echo "${ARTWORK}" | jq -r '.link')

IMAGE_URL="${IMAGE_BASE}=s${RESOLUTION}-rw"
ART_LINK="https://artsandculture.google.com/${LINK}"

echo "Selected: ${TITLE} by ${CREATOR}"

# Download image
curl -sS -o "${CURRENT_IMAGE}" "${IMAGE_URL}"

# Save metadata
cat > "${CURRENT_META}" << EOF
{
    "title": "${TITLE}",
    "creator": "${CREATOR}",
    "attribution": "${ATTRIBUTION}",
    "link": "${ART_LINK}",
    "downloaded": "$(date -Iseconds)"
}
EOF

# Update hyprpaper
if command -v hyprctl &> /dev/null; then
    hyprctl hyprpaper unload all 2>/dev/null || true
    hyprctl hyprpaper preload "${CURRENT_IMAGE}"
    hyprctl hyprpaper wallpaper ",${CURRENT_IMAGE}"
    echo "Wallpaper updated!"
fi

echo "Title: ${TITLE}"
echo "Artist: ${CREATOR}"
echo "Museum: ${ATTRIBUTION}"
echo "Link: ${ART_LINK}"
```

Make it executable:

```bash
chmod +x ~/.local/bin/google-arts-wallpaper
```

**Dependencies**: `curl`, `jq`, and `hyprpaper` (if using Hyprland).

## The Systemd Timer

To run this automatically, create a user-level systemd service and timer.

**Service** (`~/.config/systemd/user/google-arts-wallpaper.service`):

```ini
[Unit]
Description=Fetch Google Arts & Culture wallpaper
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
ExecStart=%h/.local/bin/google-arts-wallpaper
Environment=DISPLAY=:0
Environment=WAYLAND_DISPLAY=wayland-1

[Install]
WantedBy=default.target
```

**Timer** (`~/.config/systemd/user/google-arts-wallpaper.timer`):

```ini
[Unit]
Description=Daily Google Arts & Culture wallpaper update

[Timer]
OnCalendar=*-*-* 08:00:00
OnBootSec=1min
Persistent=true
RandomizedDelaySec=300

[Install]
WantedBy=timers.target
```

The timer:
- Runs daily at 8:00 AM
- Also runs 1 minute after boot (so you always have art even after a fresh start)
- Uses `Persistent=true` to catch up if the system was off at the scheduled time
- Adds a random 0-5 minute delay to avoid hammering Google's API at exactly 08:00:00

## Enable and Start

```bash
systemctl --user daemon-reload
systemctl --user enable --now google-arts-wallpaper.timer
```

To run it immediately:

```bash
systemctl --user start google-arts-wallpaper.service
```

Check the current artwork:

```bash
cat ~/.local/share/google-arts/current.json | jq
```

## What's on My Screen?

The metadata file at `~/.local/share/google-arts/current.json` includes a link to the artwork's page on Google Arts & Culture. You can add a keybind or alias to quickly open it:

```bash
alias whatart='jq -r .link ~/.local/share/google-arts/current.json | xargs xdg-open'
```

Now every morning, my desktop greets me with a different masterpiece—no browser required.
