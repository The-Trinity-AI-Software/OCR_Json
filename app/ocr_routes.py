# -*- coding: utf-8 -*-
"""
Created on Wed Apr 23 12:41:18 2025

@author: HP
"""

import os
import sys
import numpy as np
import json
from flask import Blueprint, request, jsonify, send_file, render_template
from datetime import datetime
from io import BytesIO
import base64
from PIL import Image, ImageDraw
from pdf2image import convert_from_path  # ✅ Required to process PDFs

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from app.utils import extract_text_and_structure, convert_to_json, save_layout_preview

routes = Blueprint('routes', __name__)

@routes.route("/", methods=["GET"])
def home():
    return render_template("index.html")


from io import BytesIO
import base64

@routes.route("/ocr/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    uploaded_file = request.files["file"]
    threshold = int(request.form.get("threshold", 50))
    output_format = request.form.get("format", "full")

    upload_dir = os.path.join(BASE_DIR, "..", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, uploaded_file.filename)
    uploaded_file.save(filepath)

    try:
        images = []
        if uploaded_file.filename.lower().endswith(".pdf"):
            images = convert_from_path(filepath)
        else:
            images = [Image.open(filepath).convert("RGB")]

        full_results = []
        preview_images = []

        for img in images:
            text, layout = extract_text_and_structure(img)

            # Draw bounding boxes
            draw = ImageDraw.Draw(img)
            for i in range(len(layout["text"])):
                if int(layout["conf"][i]) >= threshold and layout["text"][i].strip():
                    x, y, w, h = layout["left"][i], layout["top"][i], layout["width"][i], layout["height"][i]
                    draw.rectangle([x, y, x + w, y + h], outline="red", width=2)

            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            encoded = base64.b64encode(buffer.read()).decode("utf-8")
            preview_images.append(f"data:image/png;base64,{encoded}")

            # Convert JSON
            json_result = convert_to_json(text, layout, threshold, output_format)
            full_results.append(json_result)

        return render_template(
            "index.html",
            image_path=preview_images[0],  # just show the first page's preview
            results=json.dumps(full_results, indent=2)
        )

    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@routes.route("/ocr/save", methods=["POST"])
def save_to_storage():
    json_data = request.form["json_data"]

    # ✅ Corrected output path
    output_dir = os.path.join(BASE_DIR, "static", "output")
    os.makedirs(output_dir, exist_ok=True)

    # Create timestamped filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"output_{timestamp}.json"
    out_path = os.path.join(output_dir, filename)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(json_data)

    return f"✅ JSON successfully saved as {filename} in {output_dir}"

