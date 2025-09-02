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
    
    # التهيئة الأساسية
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'phone_store.db'),
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

app = create_app()

from cache import cached
from datetime import datetime, timedelta, time
from excel_export import ExcelExporter
from thermal_invoice import ThermalInvoiceGenerator
from forms import (
    UserForm, ProductForm, CustomerForm, SupplierForm,
    CategoryForm, BrandForm, StoreSettingsForm, ReturnForm, SaleForm
)
from dotenv import load_dotenv
import os
from io import BytesIO
from flask_wtf import CSRFProtect
from werkzeug.utils import secure_filename
from forms import UserForm, ProductForm, CustomerForm, SupplierForm, CategoryForm, BrandForm, StoreSettingsForm, ReturnForm, SaleForm
from flask_cors import CORS
import re
import json
# تم إزالة استيرادات المساعد الذكي




# دوال مساعدة لتسجيل الأنشطة
def log_activity(action, entity_type, entity_id, description=None):
    """تسجيل نشاط في السجل"""
    try:
        user_id = session.get('user_id')
        if user_id:
            activity = ActivityLog(
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                description=description
            )
            db.session.add(activity)
            db.session.commit()
    except Exception as e:
        print(f'خطأ في تسجيل النشاط: {e}')

def create_notification(user_id, notification_type, title, message, product_id=None):
    """إنشاء إشعار جديد"""
    try:
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            product_id=product_id
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    except Exception as e:
        print(f'خطأ في إنشاء الإشعار: {e}')
        return None




        edit_product_url = url_for('edit_product', product_id=1) # product_id is required for edit_product
        return f'Add Product URL: {add_product_url}<br>Edit Product URL: {edit_product_url}'"
    except Exception as e:
        return f'Error building URL: {e}'"

@app.route('/health')
def health_check():
    """فحص حالة التطبيق"""
    try:
        # فحص قاعدة البيانات
        db.session.execute('SELECT 1')
        db_status = "OK"
    except Exception as e:
        db_status = f'Error: {str(e)}'"
    
    return jsonify({
        'status': 'OK',
        'database': db_status,
        'app_env': os.environ.get('APP_ENV', 'development')
    })

@app.route('/init_database')
def init_database_route():
    """إنشاء قاعدة البيانات والجداول - للاستخدام في الإنتاج"""
    try:
        # إنشاء الجداول
        db.create_all()
        
        # إنشاء سجل إعدادات افتراضي إن لم يوجد
        if not StoreSettings.query.first():
            settings = StoreSettings()
            db.session.add(settings)
            db.session.commit()

        # إنشاء مستخدم admin افتراضي
        from werkzeug.security import generate_password_hash
        if not User.query.filter_by(username='owner').first():
            user = User(
                username='owner',                password_hash=generate_password_hash(os.environ.get('OWNER_PASSWORD', 'a_very_strong_random_password_here')),
                role='owner',
                is_active=True
            )
            db.session.add(user)
            db.session.commit()

        # إضافة بيانات تجريبية أساسية
        if not Category.query.first():
            categories = [
                Category(name='هواتف ذكية', description='الهواتف المحمولة الذكية'),
                Category(name='اكسسوارات', description='اكسسوارات الهواتف')
            ]
            for category in categories:
                db.session.add(category)
            db.session.commit()

        if not Brand.query.first():
            brands = [
                Brand(name='Samsung'),
                Brand(name='iPhone'),
                Brand(name='Huawei'),
                Brand(name='Xiaomi')
            ]
            for brand in brands:
                db.session.add(brand)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم إنشاء قاعدة البيانات بنجاح',
            'details': {
                'users_count': User.query.count(),
                'categories_count': Category.query.count(),
                'brands_count': Brand.query.count()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'خطأ في إنشاء قاعدة البيانات: {str(e)}'"
        }), 500

@app.route('/reset_database')

def reset_database_route():
    """حذف وإعادة إنشاء قاعدة البيانات - للاستخدام في حالات الطوارئ"""
    try:
        # حذف جميع الجداول
        db.drop_all()

        # إعادة إنشاء الجداول
        db.create_all()

        # إنشاء سجل إعدادات افتراضي
        settings = StoreSettings()
            db.session.add(settings)
            db.session.commit()

        # إنشاء مستخدم admin افتراضي
        from werkzeug.security import generate_password_hash
        user = User(
            username='owner',            password_hash=generate_password_hash(os.environ.get("OWNER_PASSWORD", "a_very_strong_random_password_here")),
            role='owner',
            is_active=True
        )
        db.session.add(user)
        db.session.commit()

        # إضافة بيانات تجريبية أساسية
        categories = [
            Category(name='هواتف ذكية', description='الهواتف المحمولة الذكية'),
            Category(name='اكسسوارات', description='اكسسوارات الهواتف')
        ]
        for category in categories:
            db.session.add(category)
        db.session.commit()

        brands = [
            Brand(name='Samsung'),
            Brand(name='iPhone'),
            Brand(name='Huawei'),
            Brand(name='Xiaomi')
        ]
        for brand in brands:
            db.session.add(brand)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم إعادة تعيين قاعدة البيانات بنجاح',
            'details': {
                'users_count': User.query.count(),
                'categories_count': Category.query.count(),
                'brands_count': Brand.query.count()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'خطأ في إعادة تعيين قاعدة البيانات: {str(e)}'"
        }), 500

@app.route('/database_admin')

def database_admin():
    """صفحة إدارة قاعدة البيانات"""
    return render_template('database_admin.html')

# حماية عامة: تتطلب تسجيل الدخول لكل الصفحات ما عدا تسجيل الدخول والملفات الثابتة


@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

# ==================== نظام المصادقة ====================





@app.route('/')
@cached(timeout=120, key_prefix='index_page')  # تخزين مؤقت لمدة دقيقتين
def index():
    """الصفحة الرئيسية"""
    try:
        # إحصائيات سريعة
        total_products = Product.query.count()
        total_customers = Customer.query.count()
        total_suppliers = Supplier.query.count()

        # المبيعات اليوم (استخدم نطاق زمني لتوافق أفضل بين SQLite/PostgreSQL)
        today = datetime.now().date()
        day_start = datetime.combine(today, datetime.min.time())
        day_end = day_start + timedelta(days=1)
        today_sales = Sale.query.filter(
            Sale.created_at >= day_start,
            Sale.created_at < day_end
        ).all()
        today_revenue = sum(sale.final_amount for sale in today_sales)
    except Exception as e:
        # في حالة عدم وجود جداول أو مشكلة في قاعدة البيانات
        total_products = 0
        total_customers = 0
        total_suppliers = 0
        today_sales = []
        today_revenue = 0
        flash(f'تحذير: مشكلة في قاعدة البيانات - {str(e)}', 'warning')

    try:
        # المنتجات منخفضة المخزون
        low_stock_products = Product.query.filter(
            Product.quantity <= Product.min_quantity
        ).all()

        # أحدث المبيعات
        recent_sales = Sale.query.order_by(Sale.created_at.desc()).limit(5).all()
    except Exception as e:
        low_stock_products = []
        recent_sales = []
        flash(f'تحذير: مشكلة في استعلام البيانات - {str(e)}', 'warning')

    stats = {
        'total_products': total_products,
        'total_customers': total_customers,
        'total_suppliers': total_suppliers,
        'today_revenue': today_revenue,
        'today_sales_count': len(today_sales),
        'low_stock_count': len(low_stock_products)
    }

    return render_template('index.html',
                         stats=stats,
                         low_stock_products=low_stock_products,
                         recent_sales=recent_sales)

# جعل إعدادات المتجر متاحة في جميع القوالب
@app.context_processor
def inject_store_settings():
    try:
        return {'settings': StoreSettings.query.first()}
    except Exception:
        return {'settings': None}

# إتاحة current_user في القوالب
@app.context_processor
def inject_current_user():
    try:
        uid = session.get('user_id')
        user = User.query.get(uid) if uid else None
        return {'current_user': user}
    except Exception:
        return {'current_user': None}

# إتاحة الإشعارات في القوالب
@app.context_processor
def inject_notifications():
    try:
        uid = session.get('user_id')
        if uid:
            # تحميل الإشعارات من قاعدة البيانات
            notifications = Notification.query.filter_by(user_id=uid).order_by(Notification.timestamp.desc()).limit(10).all()
            return {'notifications': notifications}
        return {'notifications': []}
    except Exception:
        return {'notifications': []}

# ==================== نظام الإشعارات ====================

@app.route('/notifications')
def notifications_page():
    """صفحة الإشعارات"""
    try:
        uid = session.get('user_id')
        if not uid:
            return redirect(url_for('index'))

        notifications = Notification.query.filter_by(user_id=uid).order_by(Notification.timestamp.desc()).all()

        # تحديد جميع الإشعارات كمقروءة
        for notification in notifications:
            notification.read = True
        db.session.commit()

        return render_template('notifications.html', notifications=notifications)
    except Exception as e:
        flash(f'خطأ في تحميل الإشعارات: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/activity_logs')
def activity_logs():
    """صفحة سجل الأنشطة"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 50
        
        logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('activity_logs.html', logs=logs)
    except Exception as e:
        flash(f'خطأ في تحميل سجل الأنشطة: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/audit_logs')
def audit_logs():
    """صفحة سجل المراجعة"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 50
        
        logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('audit_logs.html', logs=logs)
    except Exception as e:
        flash(f'خطأ في تحميل سجل المراجعة: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/notifications')
def get_notifications():
    """واجهة API للحصول على الإشعارات"""
    try:
        uid = session.get('user_id')
        if not uid:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 401

        limit = request.args.get('limit', 10, type=int)
        notifications = Notification.query.filter_by(user_id=uid).order_by(Notification.timestamp.desc()).limit(limit).all()

        return jsonify({
            'success': True,
            'notifications': [notification.to_dict() for notification in notifications]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'حدث خطأ: {str(e)}'"
        }), 500

@app.route('/notifications/mark_read/<int:notification_id>', methods=['POST'])
def mark_notification_read(notification_id):
    """تحييد إشعار كمقروء"""
    try:
        uid = session.get('user_id')
        if not uid:
            return jsonify({'success': False, 'message': 'غير مصرح'}), 401

        notification = Notification.query.filter_by(id=notification_id, user_id=uid).first()
        if not notification:
            return jsonify({'success': False, 'message': 'الإشغير موجود'}), 404

        notification.read = True
        db.session.commit()

        return jsonify({'success': True, 'message': 'تم تحديث حالة الإشعار'})

