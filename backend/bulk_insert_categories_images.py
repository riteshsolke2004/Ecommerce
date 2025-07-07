import os
from pymongo import MongoClient
from config.db_config import collection_2

# Folder containing category thumbnails
image_folder = "static/category-images"  # adjust this to your path

Quantity = "default"  # assign common category if needed

bulk_data = []

for filename in os.listdir(image_folder):
    if filename.endswith((".jpg", ".png", ".jpeg")):
        name = os.path.splitext(filename)[0]
        data = {
            "name": name,
            "path": filename,
            "Quantity": Quantity
        }
        bulk_data.append(data)

if bulk_data:
    result = collection_2.insert_many(bulk_data)
    print(f"Inserted {len(result.inserted_ids)} category images.")
else:
    print("No images found for insertion.")
