from flask import Flask
from app.ocr_routes import routes
import os
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)
app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(debug=True, port=8000)
