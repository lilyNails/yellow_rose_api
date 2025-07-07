from flask import Blueprint, request, jsonify
from src.models.database import ProductManager, CategoryManager

products_bp = Blueprint('products', __name__)
product_manager = ProductManager()
category_manager = CategoryManager()

@products_bp.route('/products', methods=['GET'])
def get_all_products():
    try:
        products = product_manager.get_all_products()
        products_list = []
        for product in products:
            products_list.append({
                'product_id': product[0],
                'name': product[1],
                'price': product[2],
                'quantity': product[3],
                'image_url': product[4],
                'category_name': product[5]
            })
        return jsonify({'success': True, 'products': products_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = product_manager.get_product_by_id(product_id)
        if product:
            return jsonify({
                'success': True,
                'product': {
                    'product_id': product[0],
                    'name': product[1],
                    'category_id': product[2],
                    'price': product[3],
                    'quantity': product[4],
                    'image_url': product[5]
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@products_bp.route('/products', methods=['POST'])
def add_product():
    try:
        data = request.get_json()
        product_id = product_manager.add_product(
            data['name'],
            data['category_id'],
            data['price'],
            data['quantity'],
            data.get('image_url')
        )
        return jsonify({'success': True, 'product_id': product_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@products_bp.route('/categories', methods=['GET'])
def get_all_categories():
    try:
        categories = category_manager.get_all_categories()
        categories_list = []
        for category in categories:
            categories_list.append({
                'category_id': category[0],
                'category_name': category[1]
            })
        return jsonify({'success': True, 'categories': categories_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@products_bp.route('/categories', methods=['POST'])
def add_category():
    try:
        data = request.get_json()
        category_id = category_manager.add_category(data['category_name'])
        return jsonify({'success': True, 'category_id': category_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

