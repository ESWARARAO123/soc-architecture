from PIL import Image, ImageDraw, ImageFont

def overlay_highlight(img_path, boxes):
    img = Image.open(img_path)
    draw = ImageDraw.Draw(img)
    for box in boxes:
        draw.rectangle(box, outline="red", width=3)
    out = img.copy()
    out_path = img_path.replace(".png", "_mod.png")
    out.save(out_path)
    return out_path
