# Project-Specific Instructions

## Font Awesome Icon Subset

This project uses a custom Font Awesome subset to reduce file size. The subset is built using `extract_icons.py`.

### When adding new icons to navbar

If you add a new icon to the navbar in `hugo.yaml`, you **must** update the icon subset:

1. **Add the icon codepoint to `extract_icons.py`:**
   - Find the Unicode codepoint for your icon in Font Awesome documentation
   - Add it to the `codepoints` list (line 30)

   Example for mastodon (U+F4F6):
   ```python
   codepoints = [0xf09b, 0xe61b, 0xe671, 0xf4f6]
   ```

2. **Rebuild the subset font:**
   ```bash
   ./extract_icons.py
   ```

   This requires `fontforge` Python module:
   ```bash
   # Install on Arch Linux
   sudo pacman -S fontforge python-fontforge

   # Or via pip
   pip install fontforge
   ```

3. **Rebuild the site:**
   ```bash
   hugo --minify
   ```

### Current icons in subset

- GitHub: U+F09B
- X/Twitter: U+E61B
- Bluesky: U+E671
- Tangled: U+F0001 (custom SVG)

### Why we use a subset

The full `fa-brands-400.woff2` is ~100KB. The subset is ~10KB, saving ~90KB on every page load.

### Custom icons

To add a custom SVG icon (like the Tangled icon):

1. Add the SVG file to the project root
2. Add an entry to `custom_svgs` dict in `extract_icons.py`:
   ```python
   custom_svgs = {
       0xf0001: "tangled-clean.svg",
       0xf0002: "your-icon.svg"  # Use private use area (0xF0000-0xFFFFD)
   }
   ```
3. Rebuild the subset as above
