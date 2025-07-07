from flask import Blueprint, request, jsonify
from config.db_config import user_collection

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/api/cart', methods=['GET'])
def get_cart():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    user = user_collection.find_one({'email': email}, {'cart': 1})
    if not user:
        return jsonify({'cart': []})

    return jsonify({'cart': user.get('cart', [])})


@cart_bp.route('/api/cart/delete', methods=['DELETE'])
def remove_from_cart():
    data = request.get_json()
    email = data.get('email')
    product_name = data.get('productName')

    if not email or not product_name:
        return jsonify({'error': 'Email and productName are required'}), 400

    user = user_collection.find_one({'email': email})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    cart = user.get('cart', [])
    new_cart = [item for item in cart if item['name'] != product_name]

    user_collection.update_one(
        {'email': email},
        {'$set': {'cart': new_cart}}
    )

    return jsonify({'message': 'Product removed from cart', 'cart': new_cart})
