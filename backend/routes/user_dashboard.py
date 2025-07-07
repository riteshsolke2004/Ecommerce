from flask import Blueprint, jsonify,request
from bson import ObjectId
from datetime import datetime
import pytz
from config.db_config import user_collection  # Use your configured collection

user_dashboard_bp = Blueprint('user_dashboard', __name__)

@user_dashboard_bp.route('/api/user-dashboard/list', methods=['GET'])
def get_all_users_for_dashboard():
    users = user_collection.find()
    user_list = []
    for i, user in enumerate(users, start=1):
        ist_time = user.get("last_active")
        if ist_time:
            ist = pytz.timezone('Asia/Kolkata')
            ist_time = ist_time.astimezone(ist).strftime('%d-%m-%Y %H:%M:%S')
        else:
            ist_time = "N/A"
        user_list.append({
            "sr": i,
            "id": str(user['_id']),
            "name": user.get("name"),
            "email": user.get("email"),
            "last_active": ist_time
        })
    return jsonify(user_list), 200

@user_dashboard_bp.route('/api/user-dashboard/delete/<user_id>', methods=['DELETE'])
def delete_user_from_dashboard(user_id):
    result = user_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 1:
        return jsonify({"message": "User deleted successfully"}), 200
    return jsonify({"message": "User not found"}), 404


# Add to cart
@user_dashboard_bp.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    data = request.json
    email = data.get('email')
    product = data.get('product')  # assume client sends product id only

    # Find user
    user = user_collection.find_one({'email': email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    cart = user.get('cart', [])

    # Check if product already in cart
    for item in cart:
        if item['product_id'] == product:
            # Increase quantity by 1
            item['quantity'] += 1
            break
    else:
        # Not in cart, add new entry
        cart.append({'product_id': product, 'quantity': 1})

    # Update user cart
    user_collection.update_one({'email': email}, {'$set': {'cart': cart}})

    return jsonify({"message": "Added to cart"}), 200


# Add to wishlist
@user_dashboard_bp.route('/add-to-wishlist', methods=['POST'])
def add_to_wishlist():
    data = request.json
    email = data.get('email')
    product = data.get('product')  # assume client sends product id only

    # Find user
    user = user_collection.find_one({'email': email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    wishlist = user.get('wishlist', [])

    # Check if product already in wishlist
    if product in wishlist:
        return jsonify({"message": "Product already in wishlist"}), 200

    # Add to wishlist
    wishlist.append(product)

    # Update user wishlist
    user_collection.update_one({'email': email}, {'$set': {'wishlist': wishlist}})

    return jsonify({"message": "Added to wishlist"}), 200


@user_dashboard_bp.route('/update-wishlist-quantity', methods=['PUT'])
def update_wishlist_quantity():
    data = request.json
    email = data.get('email')
    product_id = data.get('product_id')
    new_quantity = data.get('quantity')

    if not all([email, product_id, new_quantity]):
        return jsonify({"error": "Missing data"}), 400

    user = user_collection.find_one({'email': email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    updated_wishlist = []
    found = False

    for item in user.get('wishlist', []):
        if str(item.get('product_id', {}).get('_id')) == str(product_id):
            item['quantity'] = new_quantity
            found = True
        updated_wishlist.append(item)

    if not found:
        return jsonify({"error": "Product not found in wishlist"}), 404

    user_collection.update_one({'email': email}, {'$set': {'wishlist': updated_wishlist}})

    return jsonify({"message": "Wishlist quantity updated"}), 200



@user_dashboard_bp.route('/api/cart/delete', methods=['DELETE'])
def delete_from_cart():
    data = request.json
    email = data.get('email')
    product_id = data.get('product_id')

    if not email or not product_id:
        return jsonify({"error": "Email and product_id are required"}), 400

    try:
        user = user_collection.find_one({'email': email})
        if not user:
            return jsonify({"error": "User not found"}), 404

        updated_cart = [
            item for item in user.get('cart', [])
            if str(item.get('product_id', {}).get('_id')) != product_id
        ]

        user_collection.update_one(
            {'email': email},
            {'$set': {'cart': updated_cart}}
        )

        return jsonify({"message": "Item removed from cart"}), 200
    except Exception as e:
        print("Error deleting from cart:", e)
        return jsonify({"error": "Server error"}), 500
    
