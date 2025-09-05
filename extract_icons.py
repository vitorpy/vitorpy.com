#!/usr/bin/env fontforge

import fontforge
import os

# Open the FontAwesome brands font
font = fontforge.open("assets/fa/webfonts/fa-brands-400.ttf")

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
codepoints = [0xf09b, 0xe61b, 0xe671]

# Copy only the glyphs we need
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

# Generate the subset font files
print("\nGenerating subset fonts...")
new_font.generate("assets/fa/webfonts/fa-brands-subset.ttf")
new_font.generate("assets/fa/webfonts/fa-brands-subset.woff2")

# Check file sizes
original_size = os.path.getsize("assets/fa/webfonts/fa-brands-400.woff2")
new_size = os.path.getsize("assets/fa/webfonts/fa-brands-subset.woff2")

print(f"\nOriginal fa-brands-400.woff2: {original_size:,} bytes")
print(f"Subset fa-brands-subset.woff2: {new_size:,} bytes")
print(f"Reduction: {100 - (new_size/original_size*100):.1f}%")

font.close()
new_font.close()