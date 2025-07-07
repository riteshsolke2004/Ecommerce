from flask import Blueprint, request, jsonify
from bson import ObjectId
from config.db_config import collection
import os
from config.db_config import collection_2
# Initialize Blueprint
products_bp = Blueprint("products_bp", __name__)

# Insert a document
result = collection.insert_one({"name": "Alice", "age": 30})

# Check if insertion was successful
if result.inserted_id:
    print("Insertion successful with ID:", result.inserted_id)
else:
    print("Insertion failed")

# Confirm by querying
doc = collection.find_one({"name": "Alice"})
if doc:
    print("Found document:", doc)
else:
    print("No such document found")

# Folder where images are stored
IMAGE_URL_PATH = '/images/'
IMAGE_URL_PATH2='/category-images/'
# 🔹 Get all products
@products_bp.route('/api/collection', methods=['GET'])
def get_all_collection():
    data = list(collection.find())
    print(data)
    for item in data:
        item["_id"] = str(item["_id"])
        if 'image' in item:  # Add the full image path if available
            item['image_url'] = IMAGE_URL_PATH + item['image']
    return jsonify(data), 200

# 🔹 Get product by ID
@products_bp.route('/api/collection/<id>', methods=['GET'])
def get_product_by_id(id):
    item = collection.find_one({"_id": ObjectId(id)})
    if not item:
        return jsonify({"error": "Product not found"}), 404
    item["_id"] = str(item["_id"])
    if 'image' in item:  # Add the full image path if available
        item['image_url'] = IMAGE_URL_PATH + item['image']
    return jsonify(item), 200

# 🔹 Get products by category
@products_bp.route('/api/category-images/<category>', methods=['GET'])
def get_collection_by_category(category):
    data = list(collection_2.find({"category": category}))
    for item in data:
        item["_id"] = str(item["_id"])
        if 'path' in item:  # Use 'path' instead of 'image'
            item['image_url'] = IMAGE_URL_PATH2 + item['path']
    return jsonify(data), 200


@products_bp.route('/api/category-images/', methods=['GET'])
def get_all_category_images():
    data = list(collection_2.find())
    for item in data:
        item["_id"] = str(item["_id"])
        if 'path' in item:  # Use 'path' instead of 'image'
            item['image_url'] = IMAGE_URL_PATH2 + item['path']
    return jsonify(data), 200



