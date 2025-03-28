import os
import re
import time
import logging
from flask import Flask,Blueprint, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import PIL.Image
import cv2
import numpy as np
import google.generativeai as genai
from pdf2image import convert_from_path
from flask_socketio import emit
from socket_config import socketio 

extract_bp = Blueprint("extract", __name__)
CORS(extract_bp)

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load API Key from .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
BACKEND_API = os.getenv("BACKEND_API")

if not API_KEY:
    raise ValueError("API key not found. Set GOOGLE_API_KEY in the environment variables.")

# Configure Google Gemini API
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")



# Output folders
BASE_DIR = "processed_data"
PDF_IMAGES_DIR = os.path.join(BASE_DIR, "pdf_images")  # Folder for PDF images
CROPPED_DIR = os.path.join(os.getcwd(), "static", "cropped_questions")# Public folder for question images

os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(PDF_IMAGES_DIR, exist_ok=True)
os.makedirs(CROPPED_DIR, exist_ok=True)

def send_progress(step, percentage):
    """Emit real-time progress updates via WebSockets."""
    if socketio:
        print(f"📡 Emitting Progress: Step: {step}, Percentage: {percentage}")  # Debug log
        socketio.emit("progress", {"step": step, "progress_percent": percentage})
        socketio.sleep(1)
    else:
        print("❌ Error: SocketIO is None!")


    
# ------------------- Step 1: Convert PDF to Images -------------------
def pdf_to_images(pdf_path):
    """Convert PDF pages to images and save them in pdf_images/."""
    os.makedirs(PDF_IMAGES_DIR, exist_ok=True)  # Ensure directory exists
    send_progress("Converting PDF to Images...", 10)
    images = convert_from_path(pdf_path)
    image_paths = []

    for i, img in enumerate(images):
        image_path = os.path.join(PDF_IMAGES_DIR, f"page_{i+1}.png")
        img.save(image_path, "PNG")
        image_paths.append(image_path)

    logging.info(f"PDF converted to {len(image_paths)} images.")
    send_progress("PDF Conversion Completed", 30)
    return image_paths

# ------------------- Step 2: Extract Questions from Images -------------------
def extract_questions(image_path):
    """Extract question regions from an image using OpenCV contour detection."""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    question_images = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        
        # Filter out small noise
        if w > 100 and h > 50:
            question_img = img[y:y+h, x:x+w]
            question_images.append(question_img)

    return question_images

def save_cropped_questions(image_paths):
    """Process images and save extracted questions in static/cropped_questions/."""
    send_progress("Extracting Questions from Images...", 50)
    cropped_image_filenames = []

    for i, image_path in enumerate(image_paths):
        questions = extract_questions(image_path)

        for j, q_img in enumerate(questions):
            cropped_filename = f"question_{i+1}_{j+1}.png"
            cropped_path = os.path.join(CROPPED_DIR, cropped_filename)
            cv2.imwrite(cropped_path, q_img)
            
            # Store filename for serving images dynamically
            cropped_image_filenames.append(cropped_filename)

    logging.info(f"Saved {len(cropped_image_filenames)} cropped questions.")
    send_progress("Question Extraction Completed", 70)
    return cropped_image_filenames

# ------------------- Step 3: Extract Text Using Gemini AI -------------------
def extract_text_from_images(image_filenames, batch_size=10):
    """Extract handwritten text from cropped images using Gemini AI in batches."""
    send_progress("Extracting Text from Images...", 80)
    extracted_data = []
    os.makedirs(BASE_DIR, exist_ok=True)  # Ensure the directory exists
    text_file_path = os.path.join(BASE_DIR, "extracted_text.txt")

    with open(text_file_path, "w", encoding="utf-8") as text_file:
        for i in range(0, len(image_filenames), batch_size):
            batch = image_filenames[i:i + batch_size]
            images = []

            for filename in batch:
                try:
                    image_path = os.path.join(CROPPED_DIR, filename)
                    image = PIL.Image.open(image_path).convert("RGB")
                    images.append(image)
                except Exception as e:
                    extracted_data.append({"image_url": f"{BACKEND_API}/static/cropped_questions/{filename}", "text": f"❌ Error: {str(e)}"})
                    continue

            if not images:
                continue

            prompt = (
                "Convert the handwriting to text for each image. If needed, correct mistakes based on context. "
                "Respond with extracted text only, maintaining the order of images."
            )

            try:
                response = model.generate_content([prompt] + images)
                texts = response.text.strip().split("\n") if response.text else []

                for j, filename in enumerate(batch):
                    extracted_text = texts[j] if j < len(texts) else "No text detected"
                    extracted_data.append({"image_url": f"{BACKEND_API}/static/cropped_questions/{filename}", "text": extracted_text})
                    
                    # ✅ Save in "Image: filename | Text: extracted text" format
                    text_file.write(f"Image: {filename}\nText: {extracted_text}\n\n")

            except Exception as e:
                for filename in batch:
                    extracted_data.append({"image_url": f"{BACKEND_API}/static/cropped_questions/{filename}", "text": f"❌ AI processing failed - {str(e)}"})

            time.sleep(1)  # Avoid API rate limits
    send_progress("Text Extraction Completed", 100)
    return extracted_data



# ------------------- Flask API -------------------
@extract_bp.route("/extract-text", methods=["POST"])
def extract_text():
    """API endpoint to extract handwritten text from a PDF."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    pdf_file = request.files["file"]
    
    if pdf_file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    pdf_path = os.path.join(BASE_DIR, pdf_file.filename)
    pdf_file.save(pdf_path)

    try:
        image_paths = pdf_to_images(pdf_path)
        cropped_filenames = save_cropped_questions(image_paths)
        extracted_data = extract_text_from_images(cropped_filenames)

        return jsonify({"status": "success", "extracted_data": extracted_data})
    except Exception as e:
        logging.error(f"Processing failed: {e}")
        return jsonify({"error": str(e)}), 500

# ------------------- New Endpoints for Serving Images -------------------
@extract_bp.route("/images", methods=["GET"])
def list_images():
    """Returns a list of image URLs."""
    if not os.path.exists(CROPPED_DIR):
        return jsonify({"error": "Image directory not found"}), 404

    images = os.listdir(CROPPED_DIR)  # List all images
    image_urls = [f"http://127.0.0.1:5000/extract/images/{img}" for img in images]
    
    return jsonify({"images": image_urls})

@extract_bp.route("/extract/images/<filename>")
def get_image(filename):
    """Serve an image from the directory."""
    return send_from_directory(CROPPED_DIR, filename)










