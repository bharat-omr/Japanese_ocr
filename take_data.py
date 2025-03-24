import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib.parse import urlparse
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Create an 'uploads' folder if it doesn't exist
UPLOAD_FOLDER = "Japanese_ocr/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "Flask API is running!"

@app.route('/submit', methods=['POST'])
def submit_data():
    try:
        # Get raw data from request
        raw_data = request.json  

        # Validate that the input is a list
        if not isinstance(raw_data, list):
            return jsonify({"error": "Invalid data format, expected a list"}), 400

        processed_data = []

        # Convert JSON strings to dicts (if necessary)
        for item in raw_data:
            if isinstance(item, str):  # If it's a string, parse it
                try:
                    item = json.loads(item)
                except json.JSONDecodeError:
                    return jsonify({"error": "Invalid JSON string in list"}), 400
            
            if not isinstance(item, dict):  # Ensure it's a dictionary
                return jsonify({"error": "Invalid format, expected a JSON object"}), 400

            processed_data.append(item)  # Add the valid JSON object

        # Create a unique filename for the entire submission
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = os.path.join(UPLOAD_FOLDER, f"submission_{timestamp}.txt")

        # Open the file once and write all entries
        with open(file_path, "w", encoding="utf-8") as file:
            for item in processed_data:
                image_url = item.get("image_url")
                text = item.get("text")

                if not image_url or not text:
                    continue  # Skip invalid entries

                # Extract a valid filename from the URL for display purposes
                parsed_url = urlparse(image_url)
                image_filename = os.path.basename(parsed_url.path)

                # Write the data into the file
                file.write(f"Image Filename: {image_filename}\n")
                file.write(f"Image URL: {image_url}\n")
                file.write(f"Extracted Text: {text}\n")
                file.write("-" * 40 + "\n")  # Separator between entries

        response = {
            "message": "Data received and saved successfully!",
            "saved_file": file_path
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5003, debug=True)


