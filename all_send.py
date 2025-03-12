import os
import re
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
    """Find all images in a folder (including subfolders) and sort them numerically."""
    image_extensions = ('.png', '.jpg', '.jpeg')
    image_paths = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(image_extensions):
                image_paths.append(os.path.join(root, file))

    # **Sort numerically (question_1.png before question_10.png)**
    def extract_number(filename):
        match = re.search(r'(\d+)', filename)  # Find number in filename
        return int(match.group(1)) if match else float('inf')

    return sorted(image_paths, key=extract_number)

def extract_text_from_images(image_paths, batch_size=10):
    """
    Extract handwritten text from multiple images using Google Gemini API in batches.
    :param image_paths: List of image file paths
    :param batch_size: Number of images to process in one API call
    :return: Dictionary {image_path: extracted_text}
    """
    extracted_texts = {}
    total_images = len(image_paths)

    # Process images in batches
    for i in range(0, total_images, batch_size):
        batch = image_paths[i:i + batch_size]
        images = []

        # Load images into memory
        for file_path in batch:
            try:
                image = PIL.Image.open(file_path).convert("RGB")  # Convert to RGB for compatibility
                images.append((file_path, image))
            except Exception as e:
                extracted_texts[file_path] = f"❌ Error: Invalid image - {str(e)}"

        if not images:
            continue  # Skip if no valid images

        # Define the prompt
        prompt = (
            "Convert the handwriting to text for each image. If needed, correct mistakes based on context. "
            "Respond with extracted text only, maintaining the order of images."
        )

        # Send the batch to the API
        try:
            response = model.generate_content([prompt] + [img[1] for img in images])  # Extract only images
            texts = response.text.strip().split("\n") if response.text else []

            # Assign extracted texts to their images
            for j, (file_path, _) in enumerate(images):
                extracted_texts[file_path] = texts[j] if j < len(texts) else "No text detected"

        except Exception as e:
            for file_path, _ in images:
                extracted_texts[file_path] = f"❌ Error: AI processing failed - {str(e)}"

        # Add a delay to avoid hitting rate limits
        time.sleep(2)

    return extracted_texts

# 📌 Set the main folder containing images (Update this path)
main_folder = "data/cropped_questions"  # Change to your actual folder path

# Find all images in the folder (Sorted numerically)
image_paths = get_all_image_paths(main_folder)

# Extract text from all images in batches
extracted_texts = extract_text_from_images(image_paths, batch_size=10)

# Print extracted text in correct order
for img_path in image_paths:
    print(f"\n📄 Extracted Text from {img_path}:\n{extracted_texts.get(img_path, 'No text detected')}")
