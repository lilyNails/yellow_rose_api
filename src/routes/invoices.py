from flask import Blueprint, request, jsonify, send_file
from src.models.database import SalesManager, CustomerManager, ProductManager
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
from datetime import datetime
import tempfile

invoices_bp = Blueprint('invoices', __name__)
sales_manager = SalesManager()
customer_manager = CustomerManager()
product_manager = ProductManager()

def create_invoice_pdf(sale_data, customer_data, items_data):
    # Create a temporary file for the PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file.close()
    
    # Create PDF
    c = canvas.Canvas(temp_file.name, pagesize=A4)
    width, height = A4
    
    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawRightString(width - 50, height - 50, "يلو روز")
    c.setFont("Helvetica", 12)
    c.drawRightString(width - 50, height - 70, "Yellow Rose Flower Shop")
    
    # Invoice details
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 120, f"Invoice Number: {sale_data['invoice_number']}")
    c.drawString(50, height - 140, f"Date: {sale_data['date']}")
    c.drawString(50, height - 160, f"Payment Method: {sale_data['payment_method']}")
    
    # Customer details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 200, "Customer Details:")
    c.setFont("Helvetica", 10)
    c.drawString(70, height - 220, f"Name: {customer_data['name']}")
    c.drawString(70, height - 240, f"Phone: {customer_data['phone_number']}")
    c.drawString(70, height - 260, f"Loyalty Points: {customer_data['loyalty_points']}")
    
    # Items header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 300, "Items:")
    
    # Items table header
    y_pos = height - 330
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y_pos, "Product")
    c.drawString(200, y_pos, "Quantity")
    c.drawString(300, y_pos, "Unit Price")
    c.drawString(400, y_pos, "Total")
    
    # Draw line under header
    c.line(50, y_pos - 10, 500, y_pos - 10)
    
    # Items data
    c.setFont("Helvetica", 10)
    y_pos -= 30
    total_amount = 0
    
    for item in items_data:
        product = product_manager.get_product_by_id(item['product_id'])
        if product:
            item_total = item['quantity'] * item['unit_price']
            total_amount += item_total
            
            c.drawString(50, y_pos, product[1])  # Product name
            c.drawString(200, y_pos, str(item['quantity']))
            c.drawString(300, y_pos, f"{item['unit_price']:.2f} SAR")
            c.drawString(400, y_pos, f"{item_total:.2f} SAR")
            y_pos -= 20
    
    # Total
    c.line(50, y_pos - 10, 500, y_pos - 10)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(300, y_pos - 30, f"Total Amount: {sale_data['total_amount']:.2f} SAR")
    c.drawString(300, y_pos - 50, f"Points Earned: {sale_data['points_earned']}")
    
    # Footer
    c.setFont("Helvetica", 8)
    c.drawCentredText(width/2, 50, "Thank you for shopping with Yellow Rose!")
    c.drawCentredText(width/2, 35, "شكراً لتسوقكم مع يلو روز")
    
    c.save()
    return temp_file.name

@invoices_bp.route('/invoice/<int:sale_id>', methods=['GET'])
def generate_invoice(sale_id):
    try:
        # Get sale data
        conn = sales_manager.db.get_connection()
        cursor = conn.cursor()
        
        # Get sale details
        cursor.execute("""
            SELECT s.*, c.name, c.phone_number, c.loyalty_points
            FROM Sales s
            JOIN Customers c ON s.customer_id = c.customer_id
            WHERE s.sale_id = ?
        """, (sale_id,))
        
        sale_row = cursor.fetchone()
        if not sale_row:
            return jsonify({'success': False, 'error': 'Sale not found'}), 404
        
        sale_data = {
            'sale_id': sale_row[0],
            'invoice_number': sale_row[1],
            'date': sale_row[2],
            'customer_id': sale_row[3],
            'total_amount': sale_row[4],
            'payment_method': sale_row[5],
            'points_earned': sale_row[6]
        }
        
        customer_data = {
            'name': sale_row[7],
            'phone_number': sale_row[8],
            'loyalty_points': sale_row[9]
        }
        
        # Get sale items
        cursor.execute("""
            SELECT product_id, quantity, unit_price
            FROM Sales_Products
            WHERE sale_id = ?
        """, (sale_id,))
        
        items_data = []
        for row in cursor.fetchall():
            items_data.append({
                'product_id': row[0],
                'quantity': row[1],
                'unit_price': row[2]
            })
        
        conn.close()
        
        # Generate PDF
        pdf_path = create_invoice_pdf(sale_data, customer_data, items_data)
        
        return send_file(pdf_path, as_attachment=True, 
                        download_name=f"invoice_{sale_data['invoice_number']}.pdf",
                        mimetype='application/pdf')
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@invoices_bp.route('/invoice/latest', methods=['GET'])
def get_latest_invoice():
    try:
        # Get the latest sale
        conn = sales_manager.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT sale_id FROM Sales 
            ORDER BY date DESC 
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return generate_invoice(result[0])
        else:
            return jsonify({'success': False, 'error': 'No sales found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

