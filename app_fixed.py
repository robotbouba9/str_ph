#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تطبيق Flask لإدارة مخزون محل الهواتف - نسخة مصححة
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, make_response, send_file, session
from database import db, init_database, Product, Customer, Supplier, Sale, SaleItem, Category, PurchaseInvoice, PurchaseItem, StoreSettings, Brand, Return, ReturnItem, User
from datetime import datetime, timedelta
from excel_export import ExcelExporter
from dotenv import load_dotenv
import os
from io import BytesIO
from flask_wtf import CSRFProtect
from forms import LoginForm, UserForm, ProductForm, CustomerForm, SupplierForm, CategoryForm, BrandForm, StoreSettingsForm, ReturnForm
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# إعداد التطبيق
load_dotenv()
app = Flask(__name__)
csrf = CSRFProtect(app)
# Ensure JSON responses keep Arabic characters (no ASCII escaping)
app.config['JSON_AS_ASCII'] = False

# محاولة استيراد الإعدادات، وإذا فشلت استخدم الإعدادات الافتراضية
try:
    from config import config, MESSAGES
    env_name = os.environ.get('APP_ENV', 'development')
    app.config.from_object(config.get(env_name, config['development']))
except ImportError:
    # الإعدادات الافتراضية إذا لم يكن ملف config.py موجود
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///phone_store.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# تهيئة قاعدة البيانات
init_database(app)

# مُحدد الدور - تم تغيير اسم الدالة الداخلية لتجنب التعارض
def login_required(role=None):
    def auth_decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not session.get('user_id'):
                flash('الرجاء تسجيل الدخول للمتابعة', 'error')
                return redirect(url_for('login'))
            if role:
                user_role = session.get('user_role')
                allowed = user_role == 'admin' or user_role == role or (role == 'inventory' and user_role == 'admin')
                if not allowed:
                    flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
                    return redirect(url_for('index'))
            return fn(*args, **kwargs)
        return wrapper
    return auth_decorator

# إنشاء مستخدم افتراضي إذا لم يوجد
def ensure_admin_user():
    if not User.query.filter_by(username='admin').first():
        user = User(username='admin', password_hash=generate_password_hash('Admin@123'), role='admin', is_active=True)
        db.session.add(user)
        db.session.commit()

# تهيئة قاعدة البيانات وإنشاء المستخدم الافتراضي
with app.app_context():
    ensure_admin_user()

# صفحات المصادقة
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username, is_active=True).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_name'] = user.username
            session['user_role'] = user.role
            flash('تم تسجيل الدخول بنجاح', 'success')
            return redirect(url_for('index'))
        flash('بيانات الدخول غير صحيحة', 'error')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('login'))

# الصفحة الرئيسية
@app.route('/')
@login_required()
def index():
    # إحصائيات سريعة
    products_count = Product.query.count()
    low_stock_count = Product.query.filter(Product.quantity <= Product.min_quantity).count()
    customers_count = Customer.query.count()
    suppliers_count = Supplier.query.count()
    
    # المبيعات الأخيرة
    recent_sales = Sale.query.order_by(Sale.created_at.desc()).limit(5).all()
    
    # المنتجات الأكثر مبيعاً
    top_products = db.session.query(
        Product.id, Product.name, db.func.sum(SaleItem.quantity).label('total_sold')
    ).join(SaleItem).group_by(Product.id).order_by(db.desc('total_sold')).limit(5).all()
    
    # المنتجات منخفضة المخزون
    low_stock_products = Product.query.filter(Product.quantity <= Product.min_quantity).all()
    
    return render_template(
        'index.html',
        products_count=products_count,
        low_stock_count=low_stock_count,
        customers_count=customers_count,
        suppliers_count=suppliers_count,
        recent_sales=recent_sales,
        top_products=top_products,
        low_stock_products=low_stock_products
    )

if __name__ == '__main__':
    print("🚀 بدء تشغيل تطبيق الويب (النسخة المصححة)...")
    print("🌐 يمكنك الوصول للتطبيق على: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)