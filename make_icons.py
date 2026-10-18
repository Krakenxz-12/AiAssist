from PIL import Image

folder = "assistant/static/assistant/icons"
src = Image.open(f"{folder}/ivantill.png").convert("RGBA")
BG = (250, 60, 140, 255) 

def make(size, fill, name):
    canvas = Image.new("RGBA", (size, size), BG)
    box = int(size * fill)
    ratio = min(box / src.width, box / src.height)
    img = src.resize((int(src.width * ratio), int(src.height * ratio)), Image.LANCZOS)
    canvas.paste(img, ((size - img.width) // 2, (size - img.height) // 2), img)
    canvas.convert("RGB").save(f"{folder}/{name}")

make(192, 0.85, "icon-192.png")
make(512, 0.85, "icon-512.png")
make(512, 0.60, "icon-maskable-512.png")  