# make_icons.py
from PIL import Image, ImageDraw, ImageFont
import os

folder = "assistant/static/assistant/icons"
os.makedirs(folder, exist_ok=True)

for size in (192, 512):
    img = Image.new("RGB", (size, size), "#111111")
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=int(size * 0.45))
    d.text((size / 2, size / 2), "AI", fill="white", font=font, anchor="mm")
    img.save(f"{folder}/ivantill.png")