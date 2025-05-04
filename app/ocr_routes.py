import os
import sys
import json
import base64
from io import BytesIO
from datetime import datetime
from flask import Blueprint, request, jsonify
from PIL import Image, ImageDraw
from pdf2image import convert_from_path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from app.utils import extract_text_and_structure, convert_to_json

routes = Blueprint('routes', __name__)

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

            # Convert image to base64 for preview
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            encoded = base64.b64encode(buffer.read()).decode("utf-8")
            preview_images.append(f"data:image/png;base64,{encoded}")

            # Create structured JSON result
            json_result = convert_to_json(text, layout, threshold, output_format)
            full_results.append(json_result)

        return jsonify({
            "image": preview_images[0],  # First page only
            "results": full_results
        })

    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500


@routes.route("/ocr/save", methods=["POST"])
def save_to_storage():
    try:
        json_data = request.form["json_data"]

        output_dir = os.path.join(BASE_DIR, "static", "output")
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"output_{timestamp}.json"
        out_path = os.path.join(output_dir, filename)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(json_data)

        return jsonify({
            "message": f"✅ JSON successfully saved as {filename}",
            "filename": filename,
            "path": out_path
        })

    except Exception as e:
        return jsonify({"error": f"Save failed: {str(e)}"}), 500
