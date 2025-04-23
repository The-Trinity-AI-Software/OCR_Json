# -*- coding: utf-8 -*-
"""
Created on Wed Apr 23 12:45:00 2025

@author: HP
"""

from flask import Flask
from app.ocr_routes import routes
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ✅ THIS IS IMPORTANT:
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "app", "templates"))

app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8085)
