from flask import Flask,request,jsonify,send_from_directory
from flask_cors import CORS
from Admin.admin import admin_bp
from Products.product import products_bp
from utils.email_utils import init_mail
from routes.auth import auth_bp
from routes.admin_auth import admin_auth_bp
from routes.user_dashboard import user_dashboard_bp
from routes.Cart import cart_bp
from routes.Wishlist import wishlist_bp

app=Flask(__name__)
CORS(app)
init_mail(app)
# Serve images from static/images/
@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('static/images', filename)

@app.route('/static/category-images/<filename>')
def serve_category_image(filename):
    return send_from_directory('static/category-images', filename)

app.register_blueprint(admin_bp)
app.register_blueprint(products_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_auth_bp)
app.register_blueprint(user_dashboard_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(wishlist_bp)

if __name__ == "__main__":
    app.run(debug=True)
