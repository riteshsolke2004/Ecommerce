from flask import Blueprint, request, jsonify,json
from bson import ObjectId
from config.db_config import collection
from config.db_config import collection_2
admin_bp = Blueprint("admin", __name__)
from werkzeug.utils import secure_filename
import os

# 🔹 Add a product
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
CATEGORY_IMAGE_FOLDER = 'static/category-images'



# Function to check allowed extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/api/admin/products', methods=['POST'])
def add_product():
    # Ensure the request contains both JSON data and a file
    if 'image' not in request.files:
        return jsonify({"error": "No image part"}), 400

    image_file = request.files['image']
    
    if image_file.filename == '':
        return jsonify({"error": "No selected image"}), 400

    if image_file and allowed_file(image_file.filename):
        # Secure the filename to prevent directory traversal attacks
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)

        # Save the image file
        image_file.save(image_path)
    else:
        return jsonify({"error": "Invalid image format. Allowed formats: png, jpg, jpeg, gif"}), 400

    # Get JSON data from the frontend (using request.form for non-file fields)
    data = request.form  # This will get all the form data except files
    description = data.get("description", "{}")  # Default to an empty object if no description is provided

    # Convert description back from string to dictionary
    try:
        description = json.loads(description)
    except json.JSONDecodeError:
        return jsonify({"error": "Description must be a valid JSON object"}), 400

    product = {
        "name": data["name"],
        "path": filename,  # Save the image filename
        "rating": float(data.get("rating", 0)),
        "price": float(data.get("price", 0)),
        "description": description,  # Store the description object
        "category": data.get("category", "")
    }

    # Insert the product into the database
    result = collection.insert_one(product)

    # Return the inserted product's ID
    return jsonify({"inserted_id": str(result.inserted_id)}), 201



@admin_bp.route("/admin/bulk_add_products", methods=["POST"])
def bulk_add_products():
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({"error": "Data should be a list of product dictionaries"}), 400

        for product in data:
            # Default handling
            product.setdefault("rating", 0)
            product.setdefault("price", 0)
            product.setdefault("description", {})
            product.setdefault("category", "")
            product.setdefault("path", "")
            product.setdefault("name", "")

        result = collection.insert_many(data)
        return jsonify({
            "message": f"{len(result.inserted_ids)} products added successfully."
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Delete a product
@admin_bp.route('/api/admin/collection/<id>', methods=['DELETE'])
def delete_product(id):
    # Find product by id
    product = collection.find_one({"_id": ObjectId(id)})
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    # Get image filename from product document
    filename = product.get("path")
    if filename:
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        # Check if file exists and delete it
        if os.path.exists(image_path):
            os.remove(image_path)
        else:
            print(f"Warning: File {image_path} not found when deleting.")
    
    # Delete product from DB
    result = collection.delete_one({"_id": ObjectId(id)})
    return jsonify({"deleted": result.deleted_count}), 200

# 🔹 Update a product
@admin_bp.route("/api/admin/products/<product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.get_json()
    updated_data = {}

    # Fetch the existing product first (for merging)
    product = collection.find_one({"_id": ObjectId(product_id)})
    if not product:
        return jsonify({"error": "Product not found"}), 404

    if "name" in data:
        updated_data["name"] = data["name"]
    if "price" in data:
        updated_data["price"] = data["price"]
    if "description" in data:
        new_desc = json.loads(data["description"])
        existing_desc = product.get("description", {})
        
        if isinstance(existing_desc, dict) and isinstance(new_desc, dict):
            # Remove deleted keys from the existing description
            deleted_keys = data.get("deletedDescriptionKeys", [])
            for key in deleted_keys:
                if key in existing_desc:
                    del existing_desc[key]

            # Merge old and new descriptions
            merged_desc = {**existing_desc, **new_desc}
        else:
            merged_desc = new_desc
        
        updated_data["description"] = merged_desc
    if "image" in data:
        updated_data["image"] = data["image"]
    if "category" in data:
        updated_data["category"] = data["category"]
    if "rating" in data:
        updated_data["rating"]= data["rating"]

    if updated_data:
        collection.update_one({"_id": ObjectId(product_id)}, {"$set": updated_data})
        return jsonify({"message": "Product updated successfully"}), 200
    else:
        return jsonify({"error": "No valid fields to update"}), 400



@admin_bp.route('/admin/add_category', methods=['POST'])
def add_category_image():
    # Make sure the request includes a file part for the image
    if 'image' not in request.files:
        return jsonify({"error": "No image file part"}), 400

    image_file = request.files['image']

    if image_file.filename == '':
        return jsonify({"error": "No image selected"}), 400

    if image_file and allowed_file(image_file.filename):
        # Secure the filename
        filename = secure_filename(image_file.filename)

        # Save to category-images folder
        image_path = os.path.join('static/category-images', filename)
        image_file.save(image_path)
    else:
        return jsonify({"error": "Invalid image format. Allowed formats: png, jpg, jpeg, gif"}), 400

    # Get other fields from form data
    data = request.form
    required_fields = ['name', 'category']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Prepare the document
    category_data = {
        "name": data["name"],
        "path": filename,
        "category": data["category"]
    }

    # Insert into collection_2
    result = collection_2.insert_one(category_data)

    return jsonify({"inserted_id": str(result.inserted_id)}), 201


# Delete category image
@admin_bp.route('/admin/delete_category/<string:id>', methods=['DELETE'])
def delete_category_image(id):
    # Find the category image document first
    category_image = collection_2.find_one({'_id': ObjectId(id)})
    if not category_image:
        return jsonify({"error": "Category image not found"}), 404
    
    # Get the filename from the document
    filename = category_image.get("path")
    if filename:
        image_path = os.path.join(CATEGORY_IMAGE_FOLDER, filename)
        if os.path.exists(image_path):
            os.remove(image_path)
        else:
            print(f"Warning: Category image file {image_path} not found when deleting.")

    # Delete the document from the collection
    result = collection_2.delete_one({'_id': ObjectId(id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Failed to delete category image"}), 500

    return jsonify({"message": "Category image deleted successfully"}), 200
