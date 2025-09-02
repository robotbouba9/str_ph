from flask import (
    Flask, render_template, request, jsonify, redirect, 
    url_for, flash, make_response, session, json
)
import os

# استيراد Flask-Migrate فقط إذا كان متوفراً
try:
    from flask_migrate import Migrate
    MIGRATE_AVAILABLE = True
except ImportError:
    MIGRATE_AVAILABLE = False
from flask_wtf import CSRFProtect
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from database import (
    db, init_database, create_tables, User, Product, Sale, Category, Brand, 
    Supplier, Customer, StoreSettings, Notification, 
    ActivityLog, AuditLog, Return, ReturnItem, PurchaseInvoice,
    PurchaseItem, SaleItem
)

def create_app():
    """تطبيق Flask لإدارة مخزون محل الهواتف"""
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "phone_store.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    # تأكد من وجود مجلد 'instance'
    instance_path = os.path.join(app.instance_path)
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)

    # تهيئة الإضافات
    db.init_app(app)
    
    # تهيئة Flask-Migrate فقط إذا كان متوفراً
    if MIGRATE_AVAILABLE:
        migrate = Migrate(app, db)
    
    with app.app_context():
        # استيراد النماذج لتعمل مع Flask-Migrate
        from database import (User, StoreSettings, Category, Brand, Product, 
                            Customer, Supplier, Sale, SaleItem, Return, 
                            ReturnItem, PurchaseInvoice, PurchaseItem, 
                            Notification, ActivityLog, AuditLog)
        
        # إنشاء الجداول إذا لم تكن موجودة
        db.create_all()

        # تسجيل البلوبرينتات
        from views import main_blueprint
        app.register_blueprint(main_blueprint)

    return app

