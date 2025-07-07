import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.models.database import CategoryManager, ProductManager, UserManager, SettingsManager
import hashlib

def initialize_data():
    # Add categories
    cat_mgr = CategoryManager()
    cat_mgr.add_category('ورود طبيعية')
    cat_mgr.add_category('باقات')
    cat_mgr.add_category('هدايا')
    cat_mgr.add_category('إكسسوارات')

    # Add sample products
    prod_mgr = ProductManager()
    prod_mgr.add_product('وردة حمراء', 1, 15.00, 50)
    prod_mgr.add_product('باقة ورود مختلطة', 2, 85.00, 20)
    prod_mgr.add_product('صندوق شوكولاتة', 3, 45.00, 30)
    prod_mgr.add_product('شريط زينة', 4, 5.00, 100)

    # Add default admin user
    user_mgr = UserManager()
    password_hash = hashlib.md5('admin123'.encode()).hexdigest()
    user_mgr.add_user('admin', password_hash, 'مدير')

    # Add settings
    settings_mgr = SettingsManager()
    settings_mgr.set_setting('store_name', 'يلو روز')
    settings_mgr.set_setting('points_per_riyal', '0.1')
    settings_mgr.set_setting('notification_email', 'J8j2011@gmail.com')

    print('تم إضافة البيانات الأولية بنجاح')

if __name__ == '__main__':
    initialize_data()

