from flask import Blueprint, request, jsonify
from src.models.database import SalesManager, CustomerManager, ProductManager
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

reports_bp = Blueprint('reports', __name__)
sales_manager = SalesManager()
customer_manager = CustomerManager()
product_manager = ProductManager()

@reports_bp.route('/reports/daily', methods=['GET'])
def daily_report():
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        sales = sales_manager.get_sales_by_date(today, today)
        
        total_sales = len(sales)
        total_revenue = sum(sale[4] for sale in sales)  # total_amount is at index 4
        total_points_given = sum(sale[6] for sale in sales)  # points_earned is at index 6
        
        return jsonify({
            'success': True,
            'report': {
                'date': today,
                'total_sales': total_sales,
                'total_revenue': total_revenue,
                'total_points_given': total_points_given,
                'sales': [{
                    'invoice_number': sale[1],
                    'customer_name': sale[7],
                    'total_amount': sale[4],
                    'payment_method': sale[5],
                    'points_earned': sale[6]
                } for sale in sales]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@reports_bp.route('/reports/weekly', methods=['GET'])
def weekly_report():
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        sales = sales_manager.get_sales_by_date(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        total_sales = len(sales)
        total_revenue = sum(sale[4] for sale in sales)
        total_points_given = sum(sale[6] for sale in sales)
        
        # Group by day
        daily_breakdown = {}
        for sale in sales:
            sale_date = sale[2][:10]  # Extract date part
            if sale_date not in daily_breakdown:
                daily_breakdown[sale_date] = {
                    'sales_count': 0,
                    'revenue': 0,
                    'points_given': 0
                }
            daily_breakdown[sale_date]['sales_count'] += 1
            daily_breakdown[sale_date]['revenue'] += sale[4]
            daily_breakdown[sale_date]['points_given'] += sale[6]
        
        return jsonify({
            'success': True,
            'report': {
                'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                'total_sales': total_sales,
                'total_revenue': total_revenue,
                'total_points_given': total_points_given,
                'daily_breakdown': daily_breakdown
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@reports_bp.route('/reports/top-customers', methods=['GET'])
def top_customers_report():
    try:
        conn = customer_manager.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, phone_number, total_visits, total_purchases, loyalty_points
            FROM Customers
            ORDER BY total_purchases DESC
            LIMIT 10
        """)
        
        customers = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'top_customers': [{
                'name': customer[0],
                'phone_number': customer[1],
                'total_visits': customer[2],
                'total_purchases': customer[3],
                'loyalty_points': customer[4]
            } for customer in customers]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@reports_bp.route('/reports/inventory', methods=['GET'])
def inventory_report():
    try:
        products = product_manager.get_all_products()
        
        low_stock_products = [p for p in products if p[3] < 10]  # quantity < 10
        out_of_stock_products = [p for p in products if p[3] == 0]
        
        return jsonify({
            'success': True,
            'inventory': {
                'total_products': len(products),
                'low_stock_count': len(low_stock_products),
                'out_of_stock_count': len(out_of_stock_products),
                'products': [{
                    'product_id': product[0],
                    'name': product[1],
                    'price': product[2],
                    'quantity': product[3],
                    'category_name': product[5],
                    'status': 'out_of_stock' if product[3] == 0 else 'low_stock' if product[3] < 10 else 'in_stock'
                } for product in products],
                'low_stock_products': [{
                    'name': product[1],
                    'quantity': product[3],
                    'category_name': product[5]
                } for product in low_stock_products],
                'out_of_stock_products': [{
                    'name': product[1],
                    'category_name': product[5]
                } for product in out_of_stock_products]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def send_notification_email(subject, body, to_email="J8j2011@gmail.com"):
    """
    Send notification email (placeholder function)
    In production, you would configure SMTP settings
    """
    try:
        # This is a placeholder - in production you would configure actual SMTP
        print(f"Email notification sent to {to_email}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

@reports_bp.route('/notifications/sale', methods=['POST'])
def send_sale_notification():
    try:
        data = request.get_json()
        
        subject = f"New Sale - Invoice {data['invoice_number']}"
        body = f"""
        New sale completed at Yellow Rose:
        
        Invoice Number: {data['invoice_number']}
        Customer: {data['customer_name']} ({data['customer_phone']})
        Total Amount: {data['total_amount']} SAR
        Payment Method: {data['payment_method']}
        Points Earned: {data['points_earned']}
        Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        success = send_notification_email(subject, body)
        
        return jsonify({
            'success': success,
            'message': 'Notification sent' if success else 'Failed to send notification'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@reports_bp.route('/notifications/low-stock', methods=['POST'])
def send_low_stock_notification():
    try:
        products = product_manager.get_all_products()
        low_stock_products = [p for p in products if p[3] < 10]
        
        if not low_stock_products:
            return jsonify({'success': True, 'message': 'No low stock products'})
        
        subject = "Low Stock Alert - Yellow Rose"
        body = "The following products are running low on stock:\n\n"
        
        for product in low_stock_products:
            body += f"- {product[1]} ({product[5]}): {product[3]} units remaining\n"
        
        body += f"\nPlease restock these items soon.\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        success = send_notification_email(subject, body)
        
        return jsonify({
            'success': success,
            'low_stock_count': len(low_stock_products),
            'message': 'Low stock notification sent' if success else 'Failed to send notification'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

