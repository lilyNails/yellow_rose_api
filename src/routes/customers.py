from flask import Blueprint, request, jsonify
from src.models.database import CustomerManager

customers_bp = Blueprint('customers', __name__)
customer_manager = CustomerManager()

@customers_bp.route('/customers/phone/<phone_number>', methods=['GET'])
def get_customer_by_phone(phone_number):
    try:
        customer = customer_manager.get_customer_by_phone(phone_number)
        if customer:
            return jsonify({
                'success': True,
                'customer': {
                    'customer_id': customer[0],
                    'name': customer[1],
                    'phone_number': customer[2],
                    'total_visits': customer[3],
                    'total_purchases': customer[4],
                    'loyalty_points': customer[5],
                    'last_purchase_date': customer[6]
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@customers_bp.route('/customers', methods=['POST'])
def add_customer():
    try:
        data = request.get_json()
        customer_id = customer_manager.add_customer(
            data['name'],
            data['phone_number']
        )
        return jsonify({'success': True, 'customer_id': customer_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

