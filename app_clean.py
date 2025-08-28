from flask import Flask
from flask_migrate import Migrate
import os
from database import db, init_database

def create_app():
    """إنشاء تطبيق Flask"""
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    
    # التهيئة الأساسية
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///instance/phone_store.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    # إنشاء مجلد instance إذا لم يكن موجوداً
    os.makedirs('instance', exist_ok=True)
    
    # تهيئة قاعدة البيانات
    init_database(app)
    
    # تهيئة Flask-Migrate
    migrate = Migrate(app, db)
    
    with app.app_context():
        # استيراد النماذج
        from database import (User, StoreSettings, Category, Brand, Product, 
                            Customer, Supplier, Sale, SaleItem, Return, 
                            ReturnItem, PurchaseInvoice, PurchaseItem, 
                            Notification, ActivityLog, AuditLog)
        
        # إنشاء الجداول إذا لم تكن موجودة (للبيئة التطويرية فقط)
        if os.environ.get('FLASK_ENV') == 'development':
            db.create_all()
        
        # تسجيل البلوبرينتات
        from views import main_blueprint
        app.register_blueprint(main_blueprint)
    
    return app

# إنشاء التطبيق
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)