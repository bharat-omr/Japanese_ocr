import os
import time
import logging
from flask import Flask, jsonify,Blueprint
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

verify_bp = Blueprint("verify", __name__)
# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load API Key from .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("API key not found. Set GOOGLE_API_KEY in the environment variables.")

# Configure Google Gemini API
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")



# Directory containing the extracted text file
TEXT_DIR = "processed_data"
TEXT_FILE = os.path.join(TEXT_DIR, "extracted_text.txt")

BATCH_SIZE = 10  # Process 10 texts at a time

def verify_japanese_text(text_data):
    """Checks if Japanese text has correct meaning using Gemini AI in batches."""
    verified_results = []
    total_texts = len(text_data)

    for i in range(0, total_texts, BATCH_SIZE):
        batch = text_data[i:i + BATCH_SIZE]  # Take 10 texts at a time
        prompt_texts = [f"{j+1}. {text}" for j, text in enumerate(batch) if text.strip()]  # Numbered input

        if not prompt_texts:
            continue  # Skip empty batches

        # Structured Gemini AI prompt
        prompt = (
            "Check if the following Japanese texts are correctly extracted, including spelling and meaning accuracy.\n"
            "For each text, return 'Correct' or 'Incorrect'.\n"
            "Format your response strictly as:\n"
            "1. Correct\n"
            "2. Incorrect\n"
            "...\n\n"
            + "\n".join(prompt_texts)
        )

        try:
            response = model.generate_content(prompt)

            if not response.text:
                logging.error("AI returned an empty response.")
                results = ["AI Error"] * len(batch)
            else:
                results = response.text.strip().split("\n")

            # Ensure correct mapping between input and response
            verified_batch = []
            for j, text in enumerate(batch):
                verification = results[j].split(".")[-1].strip() if j < len(results) else "AI Error"
                verified_batch.append({"text": text, "verification": verification})

            verified_results.extend(verified_batch)

        except Exception as e:
            logging.error(f"AI processing error: {e}")
            verified_results.extend([{"text": text, "verification": "AI Processing Failed"} for text in batch])

        time.sleep(2)  # Prevent hitting API limits

    return verified_results


@verify_bp.route("/verify-japanese", methods=["GET"])
def verify_text():
    """API endpoint to read extracted_text.txt and verify Japanese text."""
    if not os.path.exists(TEXT_FILE):
        return jsonify({"error": "extracted_text.txt not found"}), 404

    try:
        with open(TEXT_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Filter out lines that start with "Image:" and keep only actual text
        text_data = [line.strip() for line in lines if line.strip() and not line.lower().startswith("image:")]

        if not text_data:
            return jsonify({"error": "No valid text found in file"}), 400

        verification_results = verify_japanese_text(text_data)
        return jsonify({"status": "success", "results": verification_results})

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500








