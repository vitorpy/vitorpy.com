#!/usr/bin/env fontforge

import fontforge
import psMat
import os

# Open the FontAwesome brands font
font = fontforge.open("themes/vitorpy/static/assets/fa/webfonts/fa-brands-400.ttf")

# Create a new font with only the icons we need
new_font = fontforge.font()

# Copy font metadata
new_font.fontname = "FontAwesome6BrandsSubset"
new_font.familyname = "Font Awesome 6 Brands Subset"
new_font.fullname = "Font Awesome 6 Brands Subset"
new_font.copyright = font.copyright
new_font.version = font.version

# Copy font metrics
new_font.ascent = font.ascent
new_font.descent = font.descent
new_font.em = font.em

# The codepoints we want to keep:
# GitHub: U+F09B (61595)
# X/Twitter: U+E61B (58907)
# Bluesky: U+E671 (58993)
# Tangled: U+F0001 (983041) - custom private use area
codepoints = [0xf09b, 0xe61b, 0xe671]
custom_svgs = {
    0xf0001: "tangled-clean.svg"  # Tangled.org icon
}

# Copy only the glyphs we need from Font Awesome
for cp in codepoints:
    if cp in font:
        # Select and copy from source font
        font.selection.select(cp)
        font.copy()

        # Create the character slot in new font
        new_font.createChar(cp)

        # Select the new slot and paste
        new_font.selection.select(("unicode",), cp)
        new_font.paste()

        print(f"Copied glyph U+{cp:04X}")

# Import custom SVG icons
for cp, svg_file in custom_svgs.items():
    if os.path.exists(svg_file):
        # Create the character slot
        glyph = new_font.createChar(cp)

        # Import the SVG
        glyph.importOutlines(svg_file)

        # Get the bounding box to calculate proper scaling
        bbox = glyph.boundingBox()
        svg_width = bbox[2] - bbox[0]
        svg_height = bbox[3] - bbox[1]

        # Scale to match Font Awesome's typical icon size (about 450-500 units)
        target_size = 450
        scale_factor = target_size / max(svg_width, svg_height)

        # Center and scale the glyph
        matrix = psMat.translate(-bbox[0], -bbox[1])  # Move to origin
        glyph.transform(matrix)
        matrix = psMat.scale(scale_factor)  # Scale to target size
        glyph.transform(matrix)

        # Center horizontally and set at baseline
        bbox_after = glyph.boundingBox()
        final_width = bbox_after[2] - bbox_after[0]
        matrix = psMat.translate((target_size - final_width) / 2, 0)
        glyph.transform(matrix)

        # Set glyph width to match typical FA icons
        glyph.width = int(target_size)

        print(f"Imported custom SVG {svg_file} as U+{cp:05X}")

# Generate the subset font files
print("\nGenerating subset fonts...")
new_font.generate("themes/vitorpy/assets/fa/webfonts/fa-brands-subset.ttf")
new_font.generate("themes/vitorpy/assets/fa/webfonts/fa-brands-subset.woff2")

# Check file sizes
original_size = os.path.getsize("themes/vitorpy/static/assets/fa/webfonts/fa-brands-400.woff2")
new_size = os.path.getsize("themes/vitorpy/assets/fa/webfonts/fa-brands-subset.woff2")

print(f"\nOriginal fa-brands-400.woff2: {original_size:,} bytes")
print(f"Subset fa-brands-subset.woff2: {new_size:,} bytes")
print(f"Reduction: {100 - (new_size/original_size*100):.1f}%")

font.close()
new_font.close()