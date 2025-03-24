import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS)

# Create an 'uploads' folder if it doesn't exist
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "Flask API is running!"

# Route to accept data and save it in a file
@app.route('/submit', methods=['POST'])
def submit_data():
    try:
        data = request.json  # Get JSON data from frontend
        image = data.get("Image")
        text = data.get("Text")

        if not image or not text:
            return jsonify({"error": "Missing name or age"}), 400

        # Save data into a text file
        file_path = os.path.join(UPLOAD_FOLDER, f"{image}.txt")
        with open(file_path, "w") as file:
            file.write(f"Name: {image}\nAge: {text}")

        response = {
            "message": "Data received and saved successfully!",
            "saved_file": file_path
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5003, debug=True)
