📌 Japanese OCR Project
Extract and translate Japanese text from images using OCR technology.

📂 Project Structure

Japanese_OCR/
│── ocr_data/                     # Stores OCR-related data
│   ├── uploads/                  # Uploaded images before processing
│   ├── processed_data/            # Processed images and extracted text
│
│── static/                        # Static files (if needed)
│
│── src/                           # Source code
│   ├── extract_image_or_text.py   # Extracts text from images
│   ├── extract_text_recheck.py    # Rechecks OCR output for accuracy
│   ├── extract_text_with_progress_bar.py # OCR with progress updates
│   ├── socket_config.py           # Manages network/socket config
│   ├── submit_data.py             # Handles data submission
│
│── .gitignore                     # Ignore unnecessary files
│── main.py                         # Entry point for the project
│── README.md                       # Documentation
│── requirements.txt                 # Dependencies
│── translate.py                     # Translates extracted text


🔹 Features
✔ Extracts Japanese text from images
✔ Rechecks and improves OCR accuracy
✔ Displays progress bar during OCR processing
✔ Supports translation of extracted text
✔ Socket-based communication support (if needed)

⚡ Installation
1️⃣ Clone the repository

git clone https://github.com/bharat-omr/Japanese_OCR.git
cd Japanese_OCR

2️⃣ Create a virtual environment (Optional but recommended)

python -m venv myenv
source myenv/bin/activate  # On Windows use: myenv\Scripts\activate

3️⃣ Install dependencies

pip install -r requirements.txt


📌 Dependencies
pytesseract – OCR engine

opencv-python – Image processing

numpy – Array handling

googletrans – Translation

socket – Networking (if needed)


![Screenshot (14)](https://github.com/user-attachments/assets/a03e1b60-40a1-4448-8644-5c378dbc4023)
![Screenshot (11)](https://github.com/user-attachments/assets/99588817-baf6-495a-96ca-d642606e8e50)
![Screenshot (13)](https://github.com/user-attachments/assets/7bc0c6b3-8634-4c8f-b34f-0ec1969782a2)
![Screenshot (15)](https://github.com/user-attachments/assets/22f4dbb6-230a-4a1d-a532-060ee83e3136)
