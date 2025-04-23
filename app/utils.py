# -*- coding: utf-8 -*-
"""
Created on Wed Apr 23 12:40:23 2025

@author: HP
"""



import pytesseract
from PIL import Image, ImageDraw
import os
from datetime import datetime

def extract_text_and_structure(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    layout = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    return text, layout

def convert_to_json(text, layout, threshold=50, format_type="full"):
    lines = [{"line": i + 1, "text": line.strip()} for i, line in enumerate(text.split("\\n")) if line.strip()]

    layout_json = []
    for i in range(len(layout.get("text", []))):
        if int(layout["conf"][i]) >= threshold and layout["text"][i].strip():
            layout_json.append({
                "text": layout["text"][i],
                "confidence": layout["conf"][i],
                "position": {
                    "left": layout["left"][i],
                    "top": layout["top"][i],
                    "width": layout["width"][i],
                    "height": layout["height"][i]
                }
            })

    if format_type == "text_only":
        return {"lines": lines}
    elif format_type == "layout_only":
        return {"layout": layout_json}
    else:
        return {"lines": lines, "layout": layout_json}

def save_layout_preview(image_path, layout, threshold, output_dir):
    

    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    for i in range(len(layout["text"])):
        if int(layout["conf"][i]) >= threshold and layout["text"][i].strip():
            x, y, w, h = layout["left"][i], layout["top"][i], layout["width"][i], layout["height"][i]
            draw.rectangle([x, y, x + w, y + h], outline="red", width=2)

    os.makedirs(output_dir, exist_ok=True)
    filename = f"preview_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
    output_path = os.path.join(output_dir, filename)
    image.save(output_path)

    # Return path relative to /static so browser can view it
    return f"static/output/{filename}"
