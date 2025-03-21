from flask import Flask, send_from_directory, jsonify
import os

app = Flask(__name__)

# Path to images directory
IMAGE_DIR = os.path.join(os.getcwd(), "static", "cropped_questions")

@app.route("/images", methods=["GET"])
def list_images():
    """Returns a list of image URLs."""
    if not os.path.exists(IMAGE_DIR):
        return jsonify({"error": "Image directory not found"}), 404

    images = os.listdir(IMAGE_DIR)  # List all images
    image_urls = [f"http://127.0.0.1:5000/image/{img}" for img in images]
    
    return jsonify({"images": image_urls})

@app.route("/image/<filename>")
def get_image(filename):
    """Serve an image from the directory."""
    return send_from_directory(IMAGE_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True)
