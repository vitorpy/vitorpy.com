# Project-Specific Instructions

## CRITICAL: DO NOT AUTO-PUSH TO PRODUCTION

**NEVER push to origin (Tangled) without explicit user confirmation.**

This repository has automatic deployment enabled. Any push to `origin` (Tangled) triggers:
1. Automatic build via Spindle CI/CD
2. Deployment to vitorpy.com
3. Sync to GitHub

**Before pushing:**
1. Build and test locally: `hugo --minify`
2. Verify changes in the `public/` directory
3. Wait for user confirmation before running `git push`
4. NEVER assume it's safe to push automatically

**Only push when the user explicitly asks you to push.**

---

## Font Awesome Icon Subset

This project uses a custom Font Awesome subset to reduce file size. The subset is built using `extract_icons.py`.

### When adding new icons to navbar

If you add a new icon to the navbar in `hugo.yaml`, you **must** update BOTH the font subset AND the CSS:

1. **Add the icon codepoint to `extract_icons.py`:**
   - Find the Unicode codepoint for your icon in Font Awesome documentation
   - Add it to the `codepoints` list (line 31)

   Example for mastodon (U+F4F6):
   ```python
   codepoints = [0xf09b, 0xe61b, 0xe671, 0xf4f6]
   ```

2. **Add the CSS rule to `themes/vitorpy/assets/css/icons.css`:**
   ```css
   .fa-mastodon::before { content: "\f4f6"; }
   ```

3. **Rebuild the subset font:**
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

4. **Test locally:**
   ```bash
   hugo serve
   ```
   Visit http://localhost:1313 and verify the icon appears in the navbar.

5. **Only after local verification, rebuild for production:**
   ```bash
   hugo --minify
   ```

### Current icons in subset

- GitHub: U+F09B
- X/Twitter: U+E61B
- Bluesky: U+E671
- Mastodon: U+F4F6 (special-cased with `rel="me"` attribute)

### Why we use a subset

The full `fa-brands-400.woff2` is ~100KB. The subset is ~10KB, saving ~90KB on every page load.

### Special navbar icon handling

**Mastodon with rel="me":**
Mastodon requires a `rel="me"` attribute for identity verification. In `hugo.yaml`, use the `mastodon` field instead of `absolute_link`:

```yaml
- name: mastodon
  mastodon: https://mathstodon.xyz/@vitorpy
```

This will render with `rel="me"` in the HTML for Mastodon identity verification.

**Other social icons:**
Use `absolute_link` for all other social media icons:

```yaml
- name: github
  absolute_link: https://github.com/vitorpy
```

### Custom SVG icons (if needed)

To add a custom SVG icon:

1. Add the SVG file to the project root
2. Add an entry to `custom_svgs` dict in `extract_icons.py`:
   ```python
   custom_svgs = {
       0xf0001: "your-icon.svg"  # Use private use area (0xF0000-0xFFFFD)
   }
   ```
3. Rebuild the subset as above
