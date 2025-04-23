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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from app.utils import extract_text_and_structure, convert_to_json, save_layout_preview

routes = Blueprint('routes', __name__)

@routes.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@routes.route("/ocr/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    uploaded_file = request.files["file"]
    threshold = int(request.form.get("threshold", 50))
    output_format = request.form.get("format", "full")

    upload_dir = os.path.join(BASE_DIR, "..", "uploads")
    static_output_dir = os.path.join(BASE_DIR, "..", "static", "output")
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(static_output_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, uploaded_file.filename)
    uploaded_file.save(filepath)

    try:
        text, layout = extract_text_and_structure(filepath)

        # ✅ This is the key line
        preview_path = save_layout_preview(filepath, layout, threshold, static_output_dir)

        results = convert_to_json(text, layout, threshold, output_format)

        return render_template(
            "index.html",
            image_path=preview_path,
            results=json.dumps(results, indent=2)
        )

    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500
    


@routes.route("/ocr/save", methods=["POST"])
def save_to_storage():
    json_data = request.form["json_data"]
    
    # Define save path
    output_dir = os.path.join(BASE_DIR, "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    # Create timestamped filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"output_{timestamp}.json"
    out_path = os.path.join(output_dir, filename)

    # Save the file
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(json_data)

    return f"✅ JSON successfully saved as {filename} in {output_dir}"

