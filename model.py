import os
import time
from dotenv import load_dotenv
import PIL.Image
import google.generativeai as genai

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("API key not found. Set GOOGLE_API_KEY in the environment variables.")

# Configure Google Gemini API
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")  # Best for images & text

def get_all_image_paths(folder_path):
    """
    Find all images in a folder (including subfolders).
    :param folder_path: Root directory containing images
    :return: List of image file paths
    """
    image_extensions = ('.png', '.jpg', '.jpeg')
    image_paths = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(image_extensions):
                image_paths.append(os.path.join(root, file))

    return image_paths

def extract_text_from_image(image_path, max_retries=3, delay=5):
    """
    Extract handwritten text from a single image using Google Gemini API.
    Retries if the API returns a 429 error (rate limit exceeded).
    
    :param image_path: Path to the image file
    :param max_retries: Number of retries in case of API failure
    :param delay: Time (seconds) to wait before retrying
    :return: Extracted text or error message
    """
    try:
        # Open and verify the image
        image = PIL.Image.open(image_path).convert("RGB")  # Convert to RGB for compatibility
    except Exception as e:
        return f"Error: Invalid image - {str(e)}"

    # Define the prompt
    prompt = "Extract hand written text from this images nothing else. If needed, correct mistakes based on context. Respond with extracted text only."

    # Retry loop in case of 429 (rate limit) errors
    for attempt in range(max_retries):
        try:
            response = model.generate_content([prompt, image])
            return response.text.strip() if response.text else "No text detected"
        except Exception as e:
            error_message = str(e)
            if "429" in error_message:
                print(f"⚠️ Rate limit exceeded! Retrying in {delay} seconds... (Attempt {attempt+1}/{max_retries})")
                time.sleep(delay)  # Wait before retrying
            else:
                return f"Error: AI processing failed - {error_message}"

    return "Error: AI processing failed after multiple attempts."

# 📌 Set the main folder containing images (Update this path)
main_folder = "data/cropped_questions"  # Change to your actual folder path

# Find all images in the folder
image_paths = get_all_image_paths(main_folder)

# Process each image one by one and print the extracted text
for img_path in image_paths:
    extracted_text = extract_text_from_image(img_path)
    print(f"\nExtracted Text from {img_path}:\n{extracted_text}")
