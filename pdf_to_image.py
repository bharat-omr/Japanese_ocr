from pdf2image import convert_from_path
import os

# Path to the uploaded PDF
pdf_path = "AI-OCR Japanese test 2 (2).pdf"

# Convert PDF to images (one image per page)
images = convert_from_path(pdf_path)

# Save images as temporary files for processing
image_paths = []
for i, img in enumerate(images):
    image_path = f"data/page_{i+1}.png"
    img.save(image_path, "PNG")
    image_paths.append(image_path)

# Return the image paths to verify before cropping
image_paths
