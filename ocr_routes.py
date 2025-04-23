# -*- coding: utf-8 -*-
"""
Created on Wed Apr 23 16:14:10 2025

@author: HP
"""


from flask import Blueprint, request, render_template
import os
import json
from app.utils import save_to_blob, save_to_sql
from app.ocr_core import ocr_process_file  # this is the function that processes pdf or image

routes = Blueprint("routes", __name__)

@routes.route("/", methods=["GET"])
def home():
    return render_template("index.html", image_path=None, results=None)

@routes.route("/ocr/convert", methods=["POST"])
def convert():
    file = request.files.get("file")
    threshold = int(request.form.get("threshold", 50))

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    file.save(file_path)

    output = ocr_process_file(file_path, threshold=threshold)

    # Save preview to Azure Blob
    blob_preview_url = save_to_blob(file_path=output["preview_path"], blob_name=os.path.basename(output["preview_path"]))
    save_to_sql(file.filename, output["json_result"], output["json_result"])

    return render_template("index.html", image_path=blob_preview_url, results=output["json_result"])

@routes.route("/ocr/save", methods=["POST"])
def save_result():
    data = request.form.get("json_data")
    filename = f"ocr_output_{os.path.getmtime(__file__)}.json"
    with open(os.path.join("output", filename), "w") as f:
        f.write(data)
    return f"✅ Saved to disk: {filename}"

