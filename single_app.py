#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تطبيق متجر الهواتف - ملف واحد فقط
- يحتوي على قاعدة البيانات (SQLAlchemy)
- صفحات الويب الأساسية (Jinja2 مضمنة داخل الكود)
- واجهة برمجية REST بسيطة لبعض الكيانات
- تسجيل الدخول/الخروج وصلاحيات بسيطة

ملاحظة:
- تم تبسيط الواجهات للحفاظ على حجم الملف.
- قاعدة البيانات تستخدم SQLite في مجلد instance/phone_store.db (إن لم يوجد سيُنشأ تلقائياً).
"""

from flask import Flask, request, redirect, url_for, render_template_string, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os
from jinja2 import DictLoader

# ------------------------------ إعداد التطبيق ------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-me-please'  # غيّرها في الإنتاج
# استخدم قاعدة بيانات ضمن مجلد instance الموجود مسبقاً بالمشروع
os.makedirs(os.path.join(os.path.dirname(__file__), 'instance'), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'instance', 'phone_store_single.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app)

# ------------------------------ نماذج قاعدة البيانات ------------------------------
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='admin')  # admin, cashier, inventory
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StoreSettings(db.Model):
    __tablename__ = 'store_settings'
    id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(200), default='MOBILE PHONE STORE')
    store_name_ar = db.Column(db.String(200), default='متجر الهواتف')
    address = db.Column(db.String(300), default='Algiers, Algeria')
    phone = db.Column(db.String(50), default='+213 123 456 789')
    currency_name = db.Column(db.String(50), default='دينار جزائري')
    currency_symbol = db.Column(db.String(10), default='د.ج')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Brand(db.Model):
    __tablename__ = 'brands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(50))
    description = db.Column(db.Text)
    price_buy = db.Column(db.Float, nullable=False)
    price_sell = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    min_quantity = db.Column(db.Integer, default=5)
    barcode = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    total_amount = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0)
    final_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default='نقدي')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# (تبسيط) عناصر البيع والمشتريات والمرتجعات يمكن إضافتها لاحقاً عند الحاجة

# ------------------------------ تهيئة القاعدة ومستخدم افتراضي ------------------------------
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(username='admin', password_hash=generate_password_hash('Admin@123'), role='admin'))
        db.session.commit()
    if not StoreSettings.query.first():
        db.session.add(StoreSettings())
        db.session.commit()

# ------------------------------ أدوات مساعدة ------------------------------
def login_required(role=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not session.get('user_id'):
                flash('الرجاء تسجيل الدخول للمتابعة', 'error')
                return redirect(url_for('login'))
            if role and session.get('user_role') not in ('admin', role):
                flash('ليس لديك صلاحية للوصول', 'error')
                return redirect(url_for('index'))
            return fn(*args, **kwargs)
        return wrapper
    return decorator

@app.context_processor
def inject_globals():
    try:
        uid = session.get('user_id')
        user = User.query.get(uid) if uid else None
        return {
            'settings': StoreSettings.query.first(),
            'current_user': user
        }
    except Exception:
        return {'settings': None, 'current_user': None}

# ------------------------------ القوالب المضمّنة ------------------------------
TEMPLATES = {
    'base.html': r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}إدارة مخزون الهواتف{% endblock %}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
</head>
<body>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container-fluid">
      <a class="navbar-brand" href="{{ url_for('index') }}">{{ settings.store_name_ar if settings else 'إدارة المخزون' }}</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#nav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="nav">
        <ul class="navbar-nav ms-auto">
          {% if current_user %}
          <li class="nav-item"><a class="nav-link" href="{{ url_for('logout') }}">تسجيل الخروج</a></li>
          {% else %}
          <li class="nav-item"><a class="nav-link" href="{{ url_for('login') }}">تسجيل الدخول</a></li>
          {% endif %}
        </ul>
      </div>
    </div>
  </nav>
  <div class="container py-4">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% for category, message in messages %}
        <div class="alert alert-{{ 'danger' if category=='error' else category }}">{{ message }}</div>
      {% endfor %}
    {% endwith %}
    <div class="row">
      <div class="col-lg-2 mb-3">
        <div class="list-group">
          <a class="list-group-item list-group-item-action" href="{{ url_for('index') }}">الرئيسية</a>
          <a class="list-group-item list-group-item-action" href="{{ url_for('products') }}">المنتجات</a>
          <a class="list-group-item list-group-item-action" href="{{ url_for('categories') }}">الفئات</a>
          <a class="list-group-item list-group-item-action" href="{{ url_for('customers') }}">العملاء</a>
          <a class="list-group-item list-group-item-action" href="{{ url_for('suppliers') }}">الموردين</a>
          <a class="list-group-item list-group-item-action" href="{{ url_for('settings_page') }}">الإعدادات</a>
          <a class="list-group-item list-group-item-action" href="{{ url_for('users_list') }}">المستخدمون</a>
        </div>
      </div>
      <div class="col-lg-10">
        {% block content %}{% endblock %}
      </div>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""",
    'login.html': r"""
{% extends 'base.html' %}
{% block title %}تسجيل الدخول{% endblock %}
{% block content %}
<div class="card mx-auto" style="max-width:420px;">
  <div class="card-header">تسجيل الدخول</div>
  <div class="card-body">
    <form method="post">
      <div class="mb-3">
        <label class="form-label">اسم المستخدم</label>
        <input name="username" class="form-control" required>
      </div>
      <div class="mb-3">
        <label class="form-label">كلمة المرور</label>
        <input type="password" name="password" class="form-control" required>
      </div>
      <button class="btn btn-primary w-100">دخول</button>
      <div class="form-text mt-2">admin / Admin@123</div>
    </form>
  </div>
</div>
{% endblock %}
""",
    'index.html': r"""
{% extends 'base.html' %}
{% block title %}الرئيسية{% endblock %}
{% block content %}
<h3 class="mb-3">لوحة التحكم</h3>
<div class="row g-3">
  <div class="col-md-3"><div class="card p-3"><b>المنتجات</b><div>{{ stats.total_products }}</div></div></div>
  <div class="col-md-3"><div class="card p-3"><b>العملاء</b><div>{{ stats.total_customers }}</div></div></div>
  <div class="col-md-3"><div class="card p-3"><b>الموردين</b><div>{{ stats.total_suppliers }}</div></div></div>
  <div class="col-md-3"><div class="card p-3"><b>منخفض المخزون</b><div>{{ stats.low_stock_count }}</div></div></div>
</div>
{% endblock %}
""",
    'products.html': r"""
{% extends 'base.html' %}
{% block title %}المنتجات{% endblock %}
{% block content %}
<div class="d-flex align-items-center justify-content-between mb-3">
  <h4>المنتجات</h4>
  <button class="btn btn-sm btn-primary" data-bs-toggle="collapse" data-bs-target="#addForm">إضافة منتج</button>
</div>
<div id="addForm" class="collapse mb-3">
  <div class="card card-body">
    <form method="post" action="{{ url_for('add_product') }}">
      <div class="row g-2">
        <div class="col-md-4"><input name="name" class="form-control" placeholder="اسم المنتج" required></div>
        <div class="col-md-2"><input name="brand" class="form-control" placeholder="الماركة" required></div>
        <div class="col-md-2"><input name="model" class="form-control" placeholder="الموديل" required></div>
        <div class="col-md-2"><input name="price_buy" class="form-control" placeholder="سعر الشراء" type="number" step="0.01" required></div>
        <div class="col-md-2"><input name="price_sell" class="form-control" placeholder="سعر البيع" type="number" step="0.01" required></div>
      </div>
      <div class="row g-2 mt-2">
        <div class="col-md-2"><input name="quantity" class="form-control" placeholder="الكمية" type="number" value="0"></div>
        <div class="col-md-2"><input name="min_quantity" class="form-control" placeholder="الحد الأدنى" type="number" value="5"></div>
        <div class="col-md-4"><input name="barcode" class="form-control" placeholder="الباركود"></div>
        <div class="col-md-4"><input name="color" class="form-control" placeholder="اللون"></div>
      </div>
      <div class="mt-2"><textarea name="description" class="form-control" placeholder="الوصف"></textarea></div>
      <div class="mt-3"><button class="btn btn-success">حفظ</button></div>
    </form>
  </div>
</div>
<div class="table-responsive">
  <table class="table table-striped">
    <thead><tr><th>#</th><th>الاسم</th><th>الماركة</th><th>الموديل</th><th>البيع</th><th>الكمية</th></tr></thead>
    <tbody>
      {% for p in products %}
      <tr>
        <td>{{ p.id }}</td>
        <td>{{ p.name }}</td>
        <td>{{ p.brand }}</td>
        <td>{{ p.model }}</td>
        <td>{{ '%.2f'|format(p.price_sell) }}</td>
        <td>{{ p.quantity }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
""",
    'categories.html': r"""
{% extends 'base.html' %}
{% block title %}الفئات{% endblock %}
{% block content %}
<h4 class="mb-3">الفئات</h4>
<form class="row g-2 mb-3" method="post" action="{{ url_for('add_category') }}">
  <div class="col-md-4"><input name="name" class="form-control" placeholder="اسم الفئة" required></div>
  <div class="col-md-6"><input name="description" class="form-control" placeholder="الوصف"></div>
  <div class="col-md-2"><button class="btn btn-success w-100">إضافة</button></div>
</form>
<ul class="list-group">
  {% for c in categories %}
  <li class="list-group-item d-flex justify-content-between align-items-center">
    <span>{{ c.name }} <small class="text-muted">{{ c.description or '' }}</small></span>
  </li>
  {% endfor %}
</ul>
{% endblock %}
""",
    'customers.html': r"""
{% extends 'base.html' %}
{% block title %}العملاء{% endblock %}
{% block content %}
<h4 class="mb-3">العملاء</h4>
<form class="row g-2 mb-3" method="post" action="{{ url_for('add_customer') }}">
  <div class="col-md-3"><input name="name" class="form-control" placeholder="الاسم" required></div>
  <div class="col-md-3"><input name="phone" class="form-control" placeholder="الهاتف"></div>
  <div class="col-md-3"><input name="email" class="form-control" placeholder="البريد"></div>
  <div class="col-md-3"><button class="btn btn-success w-100">إضافة</button></div>
</form>
<div class="table-responsive">
  <table class="table table-striped">
    <thead><tr><th>#</th><th>الاسم</th><th>الهاتف</th><th>البريد</th></tr></thead>
    <tbody>
      {% for c in customers %}
      <tr><td>{{ c.id }}</td><td>{{ c.name }}</td><td>{{ c.phone }}</td><td>{{ c.email }}</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
""",
    'suppliers.html': r"""
{% extends 'base.html' %}
{% block title %}الموردين{% endblock %}
{% block content %}
<h4 class="mb-3">الموردين</h4>
<form class="row g-2 mb-3" method="post" action="{{ url_for('add_supplier') }}">
  <div class="col-md-3"><input name="name" class="form-control" placeholder="الاسم" required></div>
  <div class="col-md-3"><input name="company" class="form-control" placeholder="الشركة"></div>
  <div class="col-md-3"><input name="phone" class="form-control" placeholder="الهاتف"></div>
  <div class="col-md-3"><button class="btn btn-success w-100">إضافة</button></div>
</form>
<div class="table-responsive">
  <table class="table table-striped">
    <thead><tr><th>#</th><th>الاسم</th><th>الشركة</th><th>الهاتف</th></tr></thead>
    <tbody>
      {% for s in suppliers %}
      <tr><td>{{ s.id }}</td><td>{{ s.name }}</td><td>{{ s.company }}</td><td>{{ s.phone }}</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
""",
    'settings.html': r"""
{% extends 'base.html' %}
{% block title %}الإعدادات{% endblock %}
{% block content %}
<h4 class="mb-3">إعدادات المتجر</h4>
<form method="post" action="{{ url_for('save_settings') }}" class="row g-2">
  <div class="col-md-4"><input name="store_name_ar" class="form-control" value="{{ settings.store_name_ar if settings }}" placeholder="اسم المتجر (عربي)"></div>
  <div class="col-md-4"><input name="address" class="form-control" value="{{ settings.address if settings }}" placeholder="العنوان"></div>
  <div class="col-md-2"><input name="phone" class="form-control" value="{{ settings.phone if settings }}" placeholder="الهاتف"></div>
  <div class="col-md-2"><button class="btn btn-primary w-100">حفظ</button></div>
</form>
{% endblock %}
""",
    'users_list.html': r"""
{% extends 'base.html' %}
{% block title %}المستخدمون{% endblock %}
{% block content %}
<h4 class="mb-3">المستخدمون</h4>
<form class="row g-2 mb-3" method="post" action="{{ url_for('user_new') }}">
  <div class="col-md-3"><input name="username" class="form-control" placeholder="اسم المستخدم" required></div>
  <div class="col-md-3"><input type="password" name="password" class="form-control" placeholder="كلمة المرور" required></div>
  <div class="col-md-3">
    <select class="form-select" name="role">
      <option value="admin">admin</option>
      <option value="cashier">cashier</option>
      <option value="inventory">inventory</option>
    </select>
  </div>
  <div class="col-md-3"><button class="btn btn-success w-100">إضافة</button></div>
</form>
<table class="table table-striped">
  <thead><tr><th>#</th><th>المستخدم</th><th>الدور</th><th>نشط</th></tr></thead>
  <tbody>
    {% for u in users %}
      <tr><td>{{ u.id }}</td><td>{{ u.username }}</td><td>{{ u.role }}</td><td>{{ '✓' if u.is_active else '✗' }}</td></tr>
    {% endfor %}
  </tbody>
</table>
{% endblock %}
""",
}

# اربط المحمل المخصص
app.jinja_loader = DictLoader(TEMPLATES)

# ------------------------------ المصادقة ------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, is_active=True).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_name'] = user.username
            session['user_role'] = user.role
            flash('تم تسجيل الدخول بنجاح', 'success')
            return redirect(url_for('index'))
        flash('بيانات الدخول غير صحيحة', 'error')
    return render_template_string(TEMPLATES['login.html'])

@app.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج', 'success')
    return redirect(url_for('login'))

# ------------------------------ الصفحة الرئيسية ------------------------------
@app.route('/')
@login_required()
def index():
    total_products = Product.query.count()
    total_customers = Customer.query.count()
    total_suppliers = Supplier.query.count()
    low_stock_count = Product.query.filter(Product.quantity <= Product.min_quantity).count()
    stats = {
        'total_products': total_products,
        'total_customers': total_customers,
        'total_suppliers': total_suppliers,
        'low_stock_count': low_stock_count,
    }
    return render_template_string(TEMPLATES['index.html'], stats=stats)

# ------------------------------ المنتجات ------------------------------
@app.route('/products')
@login_required()
def products():
    q = request.args.get('q', '')
    query = Product.query
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(Product.name.ilike(like), Product.brand.ilike(like), Product.model.ilike(like)))
    items = query.order_by(Product.created_at.desc()).all()
    return render_template_string(TEMPLATES['products.html'], products=items)

@app.route('/products/add', methods=['POST'])
@login_required('inventory')
def add_product():
    try:
        p = Product(
            name=request.form.get('name'),
            brand=request.form.get('brand'),
            model=request.form.get('model'),
            color=request.form.get('color') or '',
            description=request.form.get('description') or '',
            price_buy=float(request.form.get('price_buy', 0) or 0),
            price_sell=float(request.form.get('price_sell', 0) or 0),
            quantity=int(request.form.get('quantity', 0) or 0),
            min_quantity=int(request.form.get('min_quantity', 5) or 5),
            barcode=(request.form.get('barcode') or None),
        )
        db.session.add(p)
        db.session.commit()
        flash('تمت إضافة المنتج', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'فشل إضافة المنتج: {e}', 'error')
    return redirect(url_for('products'))

# ------------------------------ الفئات ------------------------------
@app.route('/categories')
@login_required()
def categories():
    cats = Category.query.order_by(Category.created_at.desc()).all()
    return render_template_string(TEMPLATES['categories.html'], categories=cats)

@app.route('/categories/add', methods=['POST'])
@login_required('inventory')
def add_category():
    try:
        db.session.add(Category(name=request.form.get('name'), description=request.form.get('description')))
        db.session.commit()
        flash('تمت إضافة الفئة', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'فشل إضافة الفئة: {e}', 'error')
    return redirect(url_for('categories'))

# ------------------------------ العملاء ------------------------------
@app.route('/customers')
@login_required()
def customers():
    items = Customer.query.order_by(Customer.created_at.desc()).all()
    return render_template_string(TEMPLATES['customers.html'], customers=items)

@app.route('/customers/add', methods=['POST'])
@login_required()
def add_customer():
    try:
        db.session.add(Customer(name=request.form.get('name'), phone=request.form.get('phone'), email=request.form.get('email')))
        db.session.commit()
        flash('تمت إضافة العميل', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'فشل إضافة العميل: {e}', 'error')
    return redirect(url_for('customers'))

# ------------------------------ الموردين ------------------------------
@app.route('/suppliers')
@login_required()
def suppliers():
    items = Supplier.query.order_by(Supplier.created_at.desc()).all()
    return render_template_string(TEMPLATES['suppliers.html'], suppliers=items)

@app.route('/suppliers/add', methods=['POST'])
@login_required('inventory')
def add_supplier():
    try:
        db.session.add(Supplier(name=request.form.get('name'), company=request.form.get('company'), phone=request.form.get('phone')))
        db.session.commit()
        flash('تمت إضافة المورد', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'فشل إضافة المورد: {e}', 'error')
    return redirect(url_for('suppliers'))

# ------------------------------ الإعدادات ------------------------------
@app.route('/settings')
@login_required('admin')
def settings_page():
    return render_template_string(TEMPLATES['settings.html'])

@app.route('/settings/save', methods=['POST'])
@login_required('admin')
def save_settings():
    s = StoreSettings.query.first() or StoreSettings()
    s.store_name_ar = request.form.get('store_name_ar') or s.store_name_ar
    s.address = request.form.get('address') or s.address
    s.phone = request.form.get('phone') or s.phone
    db.session.add(s)
    db.session.commit()
    flash('تم حفظ الإعدادات', 'success')
    return redirect(url_for('settings_page'))

# ------------------------------ إدارة المستخدمين ------------------------------
@app.route('/users')
@login_required('admin')
def users_list():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template_string(TEMPLATES['users_list.html'], users=users)

@app.route('/users/new', methods=['POST'])
@login_required('admin')
def user_new():
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'cashier')
        if User.query.filter_by(username=username).first():
            flash('اسم المستخدم موجود مسبقًا', 'error')
            return redirect(url_for('users_list'))
        u = User(username=username, password_hash=generate_password_hash(password), role=role, is_active=True)
        db.session.add(u)
        db.session.commit()
        flash('تمت إضافة المستخدم', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'فشل إضافة المستخدم: {e}', 'error')
    return redirect(url_for('users_list'))

# ------------------------------ واجهة برمجية (API) مبسطة ------------------------------
@app.route('/api/products', methods=['GET', 'POST'])
@login_required()
def api_products():
    if request.method == 'POST':
        data = request.get_json(force=True, silent=True) or {}
        try:
            p = Product(
                name=data.get('name'), brand=data.get('brand', ''), model=data.get('model', ''),
                color=data.get('color', ''), description=data.get('description', ''),
                price_buy=float(data.get('price_buy', 0) or 0),
                price_sell=float(data.get('price_sell', 0) or 0),
                quantity=int(data.get('quantity', 0) or 0),
                min_quantity=int(data.get('min_quantity', 5) or 5),
                barcode=data.get('barcode')
            )
            db.session.add(p)
            db.session.commit()
            return jsonify(success=True, product_id=p.id)
        except Exception as e:
            db.session.rollback()
            return jsonify(success=False, message=str(e)), 400
    # GET
    q = request.args.get('q', '')
    query = Product.query
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(Product.name.ilike(like), Product.brand.ilike(like), Product.model.ilike(like)))
    items = query.order_by(Product.created_at.desc()).all()
    return jsonify(success=True, products=[{
        'id': p.id, 'name': p.name, 'brand': p.brand, 'model': p.model,
        'price_sell': p.price_sell, 'quantity': p.quantity
    } for p in items])

@app.route('/api/customers', methods=['GET', 'POST'])
@login_required()
def api_customers():
    if request.method == 'POST':
        data = request.get_json(force=True, silent=True) or {}
        try:
            c = Customer(name=data.get('name'), phone=data.get('phone'), email=data.get('email'))
            db.session.add(c)
            db.session.commit()
            return jsonify(success=True, customer_id=c.id)
        except Exception as e:
            db.session.rollback()
            return jsonify(success=False, message=str(e)), 400
    items = Customer.query.order_by(Customer.created_at.desc()).all()
    return jsonify(success=True, customers=[{
        'id': c.id, 'name': c.name, 'phone': c.phone, 'email': c.email
    } for c in items])

# ------------------------------ تشغيل ------------------------------
if __name__ == '__main__':
    print('🚀 بدء تشغيل تطبيق الملف الواحد...')
    print('🌐 http://localhost:5000')
    app.run(debug=True, host='0.0.0.0', port=5000)