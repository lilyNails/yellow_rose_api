from flask import Blueprint, request, jsonify
from src.models.database import SalesManager, CustomerManager, ProductManager
import uuid
from datetime import datetime

sales_bp = Blueprint('sales', __name__)
sales_manager = SalesManager()
customer_manager = CustomerManager()
product_manager = ProductManager()

@sales_bp.route('/sales', methods=['POST'])
def create_sale():
    try:
        data = request.get_json()
        
        # Generate unique invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        # Get or create customer
        customer = customer_manager.get_customer_by_phone(data['customer_phone'])
        if not customer:
            customer_id = customer_manager.add_customer(data['customer_name'], data['customer_phone'])
        else:
            customer_id = customer[0]
        
        # Calculate points (1 point per 10 SAR)
        points_earned = int(data['total_amount'] / 10)
        
        # Create sale record
        sale_id = sales_manager.create_sale(
            invoice_number,
            customer_id,
            data['total_amount'],
            data['payment_method'],
            points_earned
        )
        
        # Add sale products and update inventory
        for item in data['items']:
            sales_manager.add_sale_product(
                sale_id,
                item['product_id'],
                item['quantity'],
                item['unit_price']
            )
            
            # Update product quantity
            current_product = product_manager.get_product_by_id(item['product_id'])
            if current_product:
                new_quantity = current_product[4] - item['quantity']  # quantity is at index 4
                product_manager.update_product_quantity(item['product_id'], new_quantity)
        
        # Update customer statistics
        customer_manager.update_customer_stats(customer_id, data['total_amount'], points_earned)
        
        return jsonify({
            'success': True,
            'sale_id': sale_id,
            'invoice_number': invoice_number,
            'points_earned': points_earned
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@sales_bp.route('/sales/report', methods=['GET'])
def get_sales_report():
    try:
        start_date = request.args.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        
        sales = sales_manager.get_sales_by_date(start_date, end_date)
        sales_list = []
        
        for sale in sales:
            sales_list.append({
                'sale_id': sale[0],
                'invoice_number': sale[1],
                'date': sale[2],
                'customer_id': sale[3],
                'total_amount': sale[4],
                'payment_method': sale[5],
                'points_earned': sale[6],
                'customer_name': sale[7],
                'customer_phone': sale[8]
            })
        
        return jsonify({'success': True, 'sales': sales_list})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

