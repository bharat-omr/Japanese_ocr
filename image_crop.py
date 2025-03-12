import cv2
import numpy as np
from pytesseract import pytesseract

# Function to extract questions from images
def extract_questions(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    question_images = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        
        # Filter out small noise by setting a minimum size
        if w > 100 and h > 50:
            question_img = img[y:y+h, x:x+w]
            question_images.append(question_img)

    return question_images
image_paths = 'data'
# Process each page and extract questions
cropped_questions = []
for image_path in image_paths:
    cropped_questions.extend(extract_questions(image_path))

# Save cropped question images
cropped_image_paths = []
for i, q_img in enumerate(cropped_questions):
    cropped_path = f"data/question_{i+1}.png"
    cv2.imwrite(cropped_path, q_img)
    cropped_image_paths.append(cropped_path)

# Return the cropped question image paths
cropped_image_paths
