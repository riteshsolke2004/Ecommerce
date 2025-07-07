from flask import Blueprint, request, jsonify
from config.db_config import user_collection

wishlist_bp = Blueprint('wishlist', __name__)

@wishlist_bp.route('/api/wishlist', methods=['GET'])
def get_wishlist():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    user = user_collection.find_one({'email': email}, {'wishlist': 1})
    if not user:
        return jsonify({'wishlist': []})

    return jsonify({'wishlist': user.get('wishlist', [])})


@wishlist_bp.route('/api/wishlist/delete', methods=['DELETE'])
def remove_from_wishlist():
    data = request.get_json()
    email = data.get('email')
    product_name = data.get('productName')
    print("Incoming DELETE data:", data)  # 🔍 Log incoming data


    if not email or not product_name:
        return jsonify({'error': 'Email and productName are required'}), 400

    user = user_collection.find_one({'email': email})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    wishlist = user.get('wishlist', [])
    new_wishlist = [item for item in wishlist if item.get('name') != product_name]

    user_collection.update_one(
        {'email': email},
        {'$set': {'wishlist': new_wishlist}}
    )

    return jsonify({'message': 'Product removed from wishlist', 'wishlist': new_wishlist})
