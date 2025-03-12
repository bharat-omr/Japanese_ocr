import os
import re
import time
import logging
import tempfile
from dotenv import load_dotenv
import PIL.Image
import cv2
import numpy as np
import google.generativeai as genai
from pdf2image import convert_from_path
from pytesseract import pytesseract

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load API Key from .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("API key not found. Set GOOGLE_API_KEY in the environment variables.")

# Configure Google Gemini API
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")  # Optimized for images & text

# ------------------- Step 1: Convert PDF to Images -------------------
def pdf_to_images(pdf_path, output_folder):
    """Convert PDF pages to images and save them."""
    images = convert_from_path(pdf_path)
    image_paths = []

    for i, img in enumerate(images):
        image_path = f"data/page_{i+1}.png"
        img.save(image_path, "PNG")
        image_paths.append(image_path)

    logging.info(f"PDF converted to {len(image_paths)} images.")
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

def save_cropped_questions(image_paths, output_folder):
    """Process images and save extracted questions."""
    os.makedirs(output_folder, exist_ok=True)
    cropped_image_paths = []

    for i, image_path in enumerate(image_paths):
        questions = extract_questions(image_path)

        for j, q_img in enumerate(questions):
            cropped_path = os.path.join(output_folder, f"question_{i+1}_{j+1}.png")
            cv2.imwrite(cropped_path, q_img)
            cropped_image_paths.append(cropped_path)

    logging.info(f"Saved {len(cropped_image_paths)} cropped questions.")
    return cropped_image_paths

# ------------------- Step 3: Extract Text Using Gemini AI -------------------
def get_all_image_paths(folder_path):
    """Retrieve and sort image file paths numerically."""
    image_extensions = ('.png', '.jpg', '.jpeg')
    image_paths = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(image_extensions):
                image_paths.append(os.path.join(root, file))

    def extract_number(filename):
        match = re.search(r'(\d+)', filename)
        return int(match.group(1)) if match else float('inf')

    return sorted(image_paths, key=extract_number)

def extract_text_from_images(image_paths, batch_size=10):
    """Extract handwritten text from images using Gemini AI."""
    extracted_texts = {}
    total_images = len(image_paths)

    for i in range(0, total_images, batch_size):
        batch = image_paths[i:i + batch_size]
        images = []

        for file_path in batch:
            try:
                image = PIL.Image.open(file_path).convert("RGB")
                images.append((file_path, image))
            except Exception as e:
                extracted_texts[file_path] = f"❌ Error: {str(e)}"

        if not images:
            continue

        prompt = (
            "Convert the handwriting to text for each image. If needed, correct mistakes based on context. "
            "Respond with extracted text only, maintaining the order of images."
        )

        try:
            response = model.generate_content([prompt] + [img[1] for img in images])
            texts = response.text.strip().split("\n") if response.text else []

            for j, (file_path, _) in enumerate(images):
                extracted_texts[file_path] = texts[j] if j < len(texts) else "No text detected"

        except Exception as e:
            for file_path, _ in images:
                extracted_texts[file_path] = f"❌ AI processing failed - {str(e)}"

        time.sleep(2)  # Avoid hitting API rate limits

    return extracted_texts

# ------------------- Main Execution -------------------
if __name__ == "__main__":
    pdf_path = "AI-OCR Japanese test 2 (2).pdf"

    with tempfile.TemporaryDirectory() as temp_dir:
        images_folder = os.path.join(temp_dir, "pages")
        cropped_folder = os.path.join(temp_dir, "cropped_questions")

        # Step 1: Convert PDF to Images
        image_paths = pdf_to_images(pdf_path, images_folder)

        # Step 2: Extract and Save Questions
        cropped_question_paths = save_cropped_questions(image_paths, cropped_folder)

        # Step 3: Extract Text from Cropped Images
        sorted_image_paths = get_all_image_paths(cropped_folder)
        extracted_texts = extract_text_from_images(sorted_image_paths)

        # Print Extracted Texts
        for img_path in sorted_image_paths:
            print(f"\n📄 Extracted Text from {img_path}:\n{extracted_texts.get(img_path, 'No text detected')}")
