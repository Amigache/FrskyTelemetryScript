#!/usr/bin/env python3
"""
Bitmap scaling tool for Yaapu Telemetry Widget resolution ports.
Scales all PNG images from a source resolution to a target resolution.

Usage:
    python3 tools/scale_bitmaps.py

This script scales all images from c480x272 to c800x480 using Lanczos resampling.
Full-screen overlays (minmax, warn) are scaled to exact target resolution.
HUD frame images are scaled to match the new HUD dimensions.
All other images use uniform horizontal scale factor (800/480 = 5/3).
"""

import os
import sys
from PIL import Image

# Source and target screen dimensions
SRC_W, SRC_H = 480, 272
DST_W, DST_H = 800, 480

# Scale factors
SX = DST_W / SRC_W  # 1.6667
SY = DST_H / SRC_H  # 1.7647

# Source HUD and target HUD dimensions
SRC_HUD_W, SRC_HUD_H = 240, 130
DST_HUD_W, DST_HUD_H = 400, 230

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
SRC_DIR = os.path.join(BASE_DIR, "OTX_ETX", "c480x272", "SD", "WIDGETS", "yaapu", "images")
DST_DIR = os.path.join(BASE_DIR, "OTX_ETX", "c800x480", "SD", "WIDGETS", "yaapu", "images")

# Special-case images with exact target dimensions
EXACT_SIZES = {
    # Full-screen overlays → exact new screen size
    "minmax.png": (DST_W, DST_H),
    "warn.png": (DST_W, DST_H),
    # HUD frame/background → match new HUD area
    "hud.png": (DST_HUD_W, DST_HUD_H),
    "hud_bg.png": (DST_HUD_W, DST_HUD_H),
}


def scale_image(src_path, dst_path, filename):
    """Scale a single image file."""
    img = Image.open(src_path)
    orig_w, orig_h = img.size

    if filename in EXACT_SIZES:
        new_w, new_h = EXACT_SIZES[filename]
    else:
        # Uniform scale using horizontal factor for width, vertical factor for height
        new_w = round(orig_w * SX)
        new_h = round(orig_h * SY)

    # Choose resampling method based on image mode
    if img.mode == "P":
        # Palette mode: convert to RGBA for quality scaling, then convert back
        img_rgba = img.convert("RGBA")
        img_scaled = img_rgba.resize((new_w, new_h), Image.LANCZOS)
        # Convert back to palette mode with transparency
        img_scaled = img_scaled.quantize(colors=256)
    elif img.mode == "RGB":
        img_scaled = img.resize((new_w, new_h), Image.LANCZOS)
    else:
        # RGBA - direct Lanczos
        img_scaled = img.resize((new_w, new_h), Image.LANCZOS)

    img_scaled.save(dst_path, "PNG", optimize=True)
    return orig_w, orig_h, new_w, new_h


def main():
    if not os.path.isdir(SRC_DIR):
        print(f"ERROR: Source directory not found: {SRC_DIR}")
        sys.exit(1)

    os.makedirs(DST_DIR, exist_ok=True)

    png_files = sorted(f for f in os.listdir(SRC_DIR) if f.lower().endswith(".png"))
    print(f"Scaling {len(png_files)} images from {SRC_W}x{SRC_H} to {DST_W}x{DST_H}")
    print(f"  Horizontal scale: {SX:.4f}")
    print(f"  Vertical scale:   {SY:.4f}")
    print(f"  HUD: {SRC_HUD_W}x{SRC_HUD_H} -> {DST_HUD_W}x{DST_HUD_H}")
    print()

    for filename in png_files:
        src_path = os.path.join(SRC_DIR, filename)
        dst_path = os.path.join(DST_DIR, filename)
        try:
            ow, oh, nw, nh = scale_image(src_path, dst_path, filename)
            tag = " [EXACT]" if filename in EXACT_SIZES else ""
            print(f"  {filename:40s} {ow:4d}x{oh:<4d} -> {nw:4d}x{nh:<4d}{tag}")
        except Exception as e:
            print(f"  {filename:40s} ERROR: {e}")

    print(f"\nDone! Scaled images written to: {DST_DIR}")


if __name__ == "__main__":
    main()
