import os
from pymongo import MongoClient
from config.db_config import collection


# Path to your image folder
IMAGE_FOLDER = "images"  # change this to your actual folder path

# List all image files
image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

# Create product documents
documents = []
for img in image_files:
    doc = {
        "name": os.path.splitext(img)[0],  # name from filename
        "path": img,                       # image path (same as name for now)
        "rating": 0,
        "price": 0,
        "description": {},                # empty dict
        "category": ""                    # empty string
    }
    documents.append(doc)

# Bulk insert
if documents:
    result = collection.insert_many(documents)
    print(f"Inserted {len(result.inserted_ids)} images.")
else:
    print("No image files found.")
