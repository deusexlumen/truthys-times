#!/usr/bin/env python3
"""Generate OG Banner for Truthy's Times"""
from PIL import Image, ImageDraw, ImageFont
import os

WIDTH, HEIGHT = 1200, 630
BG_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
ACCENT = (220, 50, 32)  # Rot

def make_banner(output_path="assets/og-banner.png", edition="008", date="2026-05-23"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts, fallback to default
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        font_mid = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font_large = ImageFont.load_default()
        font_mid = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Accent line
    draw.rectangle([40, 40, 1160, 44], fill=ACCENT)
    
    # Title
    draw.text((60, 80), "TRUTHY'S TIMES", fill=TEXT_COLOR, font=font_large)
    
    # Subtitle
    draw.text((60, 180), "Signal-Zeitung für Tech, Wissenschaft & digitale Kultur", fill=(180,180,180), font=font_small)
    
    # Edition info
    draw.text((60, 320), f"Ausgabe #{edition}", fill=ACCENT, font=font_mid)
    draw.text((60, 380), date, fill=(200,200,200), font=font_small)
    
    # Bottom line
    draw.text((60, 540), "Kuratiert von Truthseeker v6.4", fill=(100,100,100), font=font_small)
    draw.rectangle([40, 590, 1160, 594], fill=ACCENT)
    
    img.save(output_path)
    print(f"[OK] OG Banner saved to {output_path}")

if __name__ == "__main__":
    import sys
    edition = sys.argv[1] if len(sys.argv) > 1 else "008"
    date = sys.argv[2] if len(sys.argv) > 2 else "2026-05-23"
    make_banner(edition=edition, date=date)
