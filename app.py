# -*- coding: utf-8 -*-
"""
تطبيق Flask لإدارة مخزون محل الهواتف
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, make_response, send_file
from database import db, init_database, Product, Customer, Supplier, Sale, SaleItem, Category, PurchaseInvoice, PurchaseItem, StoreSettings, Brand, Return, ReturnItem, User
from datetime import datetime, timedelta
from excel_export import ExcelExporter
from dotenv import load_dotenv
import os
from io import BytesIO
from flask_wtf import CSRFProtect
from forms import LoginForm, UserForm, ProductForm, CustomerForm, SupplierForm, CategoryForm, BrandForm, StoreSettingsForm, ReturnForm

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

# ==================== فلاتر Jinja2 ====================
@app.template_filter('english_numbers')
def english_numbers(value):
    """تحويل الأرقام الهندية العربية إلى أرقام إنجليزية"""
    try:
        s = str(value)
        return s.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))
    except Exception:
        return str(value)

@app.template_filter('currency')
def currency(value):
    """تنسيق العملة مع الفاصلة العشرية والرمز"""
    try:
        num = float(value or 0)
    except (ValueError, TypeError):
        num = 0.0
    symbol = 'د.ج'
    try:
        settings = StoreSettings.query.first()
        if settings and getattr(settings, 'currency_symbol', None):
            symbol = settings.currency_symbol
    except Exception:
        pass
    return f"{num:,.2f} {symbol}"

# جلسات للمصادقة
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import session

# مُحدد الدور
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

# Register the function to run when the app starts
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
    flash('تم تسجيل الخروج', 'success')
    return redirect(url_for('login'))

# حماية عامة: تتطلب تسجيل الدخول لكل الصفحات ما عدا تسجيل الدخول والملفات الثابتة
@app.before_request
def _require_login():
    if request.endpoint in ('login', 'static'):
        return
    if not session.get('user_id'):
        # API تفضّل JSON عندما يطلب العميل JSON
        if request.accept_mimetypes and request.accept_mimetypes['application/json'] > request.accept_mimetypes['text/html']:
            return jsonify(success=False, message='Unauthorized'), 401
        return redirect(url_for('login'))

@app.route('/')
@login_required()
def index():
    """الصفحة الرئيسية"""
    # إحصائيات سريعة
    total_products = Product.query.count()
    total_customers = Customer.query.count()
    total_suppliers = Supplier.query.count()
    
    # المبيعات اليوم
    today = datetime.now().date()
    today_sales = Sale.query.filter(
        db.func.date(Sale.created_at) == today
    ).all()
    today_revenue = sum(sale.final_amount for sale in today_sales)
    
    # المنتجات منخفضة المخزون
    low_stock_products = Product.query.filter(
        Product.quantity <= Product.min_quantity
    ).all()
    
    # أحدث المبيعات
    recent_sales = Sale.query.order_by(Sale.created_at.desc()).limit(5).all()
    
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

# ==================== إدارة المستخدمين ====================

@app.route('/users')
@login_required('admin')
def users_list():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('users_list.html', users=users)

@app.route('/users/new', methods=['GET', 'POST'])
@login_required('admin')
def user_new():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        role = form.role.data
        is_active = form.is_active.data

        if User.query.filter_by(username=username).first():
            flash('اسم المستخدم موجود مسبقًا', 'error')
            return redirect(url_for('user_new'))

        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role=role,
            is_active=is_active
        )
        db.session.add(user)
        db.session.commit()
        flash('تم إضافة المستخدم بنجاح', 'success')
        return redirect(url_for('users_list'))

    return render_template('user_form.html', form=form, user=None)

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required('admin')
def user_edit(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        user.role = form.role.data
        user.is_active = form.is_active.data
        db.session.commit()
        flash('تم تحديث المستخدم بنجاح', 'success')
        return redirect(url_for('users_list'))
    return render_template('user_form.html', form=form, user=user)

@app.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required('admin')
def user_toggle(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    flash('تم تحديث حالة المستخدم', 'success')
    return redirect(url_for('users_list'))

# ==================== إدارة المنتجات ====================

@app.route('/brands')
def brands():
    """صفحة الماركات"""
    brands = Brand.query.order_by(Brand.name.asc()).all()
    return render_template('brands.html', brands=brands)

# API بسيطة للبحث بالباركود (POS)
@app.route('/api/products/barcode/<barcode>')
def api_product_by_barcode(barcode):
    try:
        product = Product.query.filter_by(barcode=barcode).first()
        if not product:
            return jsonify(success=False, message='الباركود غير موجود'), 404
        return jsonify(success=True, product=product.to_dict())
    except Exception as e:
        return jsonify(success=False, message=str(e)), 400

@app.route('/products')
def products():
    """صفحة المنتجات"""
    search = request.args.get('search', '')
    brand = request.args.get('brand', '')
    category = request.args.get('category', '')
    
    query = Product.query
    
    if search:
        # بحث محسن يدعم البحث الجزئي والمرن
        search_terms = search.split()
        for term in search_terms:
            query = query.filter(
                db.or_(
                    Product.name.ilike(f'%{term}%'),
                    Product.model.ilike(f'%{term}%'),
                    Product.brand.ilike(f'%{term}%'),
                    Product.description.ilike(f'%{term}%'),
                    Product.barcode.ilike(f'%{term}%')
                )
            )
    
    if brand:
        query = query.filter(Product.brand == brand)
    
    if category:
        query = query.filter(Product.category_id == category)
    
    products = query.order_by(Product.created_at.desc()).all()
    # اجلب قائمة الماركات من جدول الماركات
    brands = [b.name for b in Brand.query.order_by(Brand.name.asc()).all()]
    categories = Category.query.all()
    
    return render_template('products.html', products=products, brands=brands, categories=categories)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        image_filename = None
        if form.image.data and allowed_file(form.image.data.filename):
            image_filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        new_product = Product(name=form.name.data, brand=form.brand.data, model=form.model.data, color=form.color.data,
                              description=form.description.data, price_buy=form.price_buy.data, price_sell=form.price_sell.data,
                              quantity=form.quantity.data, min_quantity=form.min_quantity.data, barcode=form.barcode.data,
                              imei=form.imei.data, warranty_period=form.warranty_period.data,
                              category_id=form.category_id.data, supplier_id=form.supplier_id.data)
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('products'))
    elif request.method == 'POST':
        flash('Form validation failed. Please check your inputs.', 'danger')

    categories = Category.query.all()
    brands = Brand.query.all()
    suppliers = Supplier.query.all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    form.brand_id.choices = [(b.id, b.name) for b in brands]
    form.supplier_id.choices = [(s.id, s.name) for s in suppliers]
    return render_template('add_product.html', form=form, categories=categories, brands=brands, suppliers=suppliers)

@app.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required()
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        if form.image.data and allowed_file(form.image.data.filename):
            if product.image:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], product.image))
                except OSError as e:
                    app.logger.error(f"Error deleting old image: {e}")
            image_filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            product.image = image_filename
        elif form.image.data is None and 'image-clear' in request.form: # Handle image clearing
            if product.image:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], product.image))
                except OSError as e:
                    app.logger.error(f"Error deleting old image: {e}")
                product.image = None

        product.name = form.name.data
        product.brand = form.brand.data
        product.model = form.model.data
        product.color = form.color.data
        product.description = form.description.data
        product.price_buy = form.price_buy.data
        product.price_sell = form.price_sell.data
        product.quantity = form.quantity.data
        product.min_quantity = form.min_quantity.data
        product.barcode = form.barcode.data
        product.imei = form.imei.data
        product.warranty_period = form.warranty_period.data
        product.category_id = form.category_id.data
        product.supplier_id = form.supplier_id.data
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products'))
    elif request.method == 'POST':
        flash('Form validation failed. Please check your inputs.', 'danger')

    categories = Category.query.all()
    brands = Brand.query.all()
    suppliers = Supplier.query.all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    form.brand_id.choices = [(b.id, b.name) for b in brands]
    form.supplier_id.choices = [(s.id, s.name) for s in suppliers]
    return render_template('edit_product.html', form=form, product=product, categories=categories, brands=brands, suppliers=suppliers)

@app.route('/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    """حذف منتج"""
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        flash('تم حذف المنتج بنجاح', 'success')
    except Exception as e:
        flash(f'خطأ في حذف المنتج: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('products'))

# ==================== إدارة الفئات ====================

@app.route('/categories')
def categories():
    """صفحة الفئات"""
    categories = Category.query.order_by(Category.created_at.desc()).all()
    return render_template('categories.html', categories=categories)

@app.route('/categories/add', methods=['GET', 'POST'])
@login_required()
def add_category():
    """إضافة فئة"""
    form = CategoryForm()
    if form.validate_on_submit():
        try:
            category = Category(
                name=form.name.data,
                description=form.description.data
            )
            
            db.session.add(category)
            db.session.commit()
            flash('تم إضافة الفئة بنجاح', 'success')
            return redirect(url_for('categories'))
            
        except Exception as e:
            flash(f'خطأ في إضافة الفئة: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('add_category.html', form=form)

@app.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required()
def edit_category(category_id):
    """تعديل فئة"""
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(category)
            
            db.session.commit()
            flash('تم تحديث الفئة بنجاح', 'success')
            return redirect(url_for('categories'))
            
        except Exception as e:
            flash(f'خطأ في تحديث الفئة: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('edit_category.html', category=category, form=form)

@app.route('/categories/delete/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    """حذف فئة"""
    try:
        category = Category.query.get_or_404(category_id)
        
        # التحقق من وجود منتجات مرتبطة بهذه الفئة
        if category.products:
            flash('لا يمكن حذف هذه الفئة لأنها مرتبطة بمنتجات', 'error')
        else:
            db.session.delete(category)
            db.session.commit()
            flash('تم حذف الفئة بنجاح', 'success')
    except Exception as e:
        flash(f'خطأ في حذف الفئة: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('categories'))

# ==================== إدارة العملاء ====================

@app.route('/customers')
def customers():
    """صفحة العملاء"""
    search = request.args.get('search', '')
    
    query = Customer.query
    
    if search:
        query = query.filter(
            db.or_(
                Customer.name.contains(search),
                Customer.phone.contains(search),
                Customer.email.contains(search)
            )
        )
    
    customers = query.order_by(Customer.created_at.desc()).all()
    return render_template('customers.html', customers=customers)

@app.route('/customers/add', methods=['GET', 'POST'])
@login_required()
def add_customer():
    """إضافة عميل جديد"""
    form = CustomerForm()
    if form.validate_on_submit():
        try:
            customer = Customer(
                name=form.name.data,
                phone=form.phone.data,
                email=form.email.data,
                address=form.address.data
            )
            
            db.session.add(customer)
            db.session.commit()
            flash('تم إضافة العميل بنجاح', 'success')
            return redirect(url_for('customers'))
            
        except Exception as e:
            flash(f'خطأ في إضافة العميل: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('add_customer.html', form=form)

@app.route('/customers/edit/<int:customer_id>', methods=['GET', 'POST'])
@login_required()
def edit_customer(customer_id):
    """تعديل عميل"""
    customer = Customer.query.get_or_404(customer_id)
    form = CustomerForm(obj=customer)
    if form.validate_on_submit():
        try:
            form.populate_obj(customer)
            
            db.session.commit()
            flash('تم تحديث العميل بنجاح', 'success')
            return redirect(url_for('customers'))
            
        except Exception as e:
            flash(f'خطأ في تحديث العميل: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('edit_customer.html', customer=customer, form=form)

@app.route('/customers/delete/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    """حذف عميل"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        flash('تم حذف العميل بنجاح', 'success')
    except Exception as e:
        flash(f'خطأ في حذف العميل: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('customers'))

# ==================== إدارة الموردين ====================

@app.route('/suppliers')
def suppliers():
    """صفحة الموردين"""
    search = request.args.get('search', '')
    
    query = Supplier.query
    
    if search:
        query = query.filter(
            db.or_(
                Supplier.name.contains(search),
                Supplier.company.contains(search),
                Supplier.phone.contains(search)
            )
        )
    
    suppliers = query.order_by(Supplier.created_at.desc()).all()
    return render_template('suppliers.html', suppliers=suppliers)

@app.route('/suppliers/add', methods=['GET', 'POST'])
@login_required()
def add_supplier():
    """إضافة مورد جديد"""
    form = SupplierForm()
    if form.validate_on_submit():
        try:
            supplier = Supplier(
                name=form.name.data,
                company=form.company.data,
                phone=form.phone.data,
                email=form.email.data,
                address=form.address.data
            )
            
            db.session.add(supplier)
            db.session.commit()
            flash('تم إضافة المورد بنجاح', 'success')
            return redirect(url_for('suppliers'))
            
        except Exception as e:
            flash(f'خطأ في إضافة المورد: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('add_supplier.html', form=form)

@app.route('/brands/add', methods=['GET', 'POST'])
@login_required()
def add_brand():
    """إضافة ماركة جديدة"""
    form = BrandForm()
    if form.validate_on_submit():
        try:
            brand_name = form.name.data.strip()
            if not brand_name:
                flash('اسم الماركة لا يمكن أن يكون فارغًا', 'error')
                return redirect(url_for('add_brand'))

            existing_brand = Brand.query.filter_by(name=brand_name).first()
            if existing_brand:
                flash('هذه الماركة موجودة بالفعل', 'error')
                return redirect(url_for('add_brand'))

            brand = Brand(name=brand_name)
            db.session.add(brand)
            db.session.commit()
            flash('تم إضافة الماركة بنجاح', 'success')
            return redirect(url_for('brands'))
        except Exception as e:
            flash(f'خطأ في إضافة الماركة: {str(e)}', 'error')
            db.session.rollback()
    return render_template('add_brand.html', form=form)

@app.route('/brands/delete/<int:brand_id>', methods=['POST'])
def delete_brand(brand_id):
    """حذف ماركة"""
    try:
        brand = Brand.query.get_or_404(brand_id)
        db.session.delete(brand)
        db.session.commit()
        flash('تم حذف الماركة بنجاح', 'success')
    except Exception as e:
        flash(f'خطأ في حذف الماركة: {str(e)}', 'error')
        db.session.rollback()
    return redirect(url_for('brands'))

@app.route('/suppliers/edit/<int:supplier_id>', methods=['GET', 'POST'])
@login_required()
def edit_supplier(supplier_id):
    """تعديل مورد"""
    supplier = Supplier.query.get_or_404(supplier_id)
    form = SupplierForm(obj=supplier)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(supplier)
            
            db.session.commit()
            flash('تم تحديث المورد بنجاح', 'success')
            return redirect(url_for('suppliers'))
            
        except Exception as e:
            flash(f'خطأ في تحديث المورد: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('edit_supplier.html', supplier=supplier, form=form)

@app.route('/suppliers/delete/<int:supplier_id>', methods=['POST'])
def delete_supplier(supplier_id):
    """حذف مورد"""
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        db.session.delete(supplier)
        db.session.commit()
        flash('تم حذف المورد بنجاح', 'success')
    except Exception as e:
        flash(f'خطأ في حذف المورد: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('suppliers'))

# ==================== إدارة المبيعات ====================

@app.route('/sales')
def sales():
    """صفحة المبيعات"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    sales = Sale.query.order_by(Sale.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('sales.html', sales=sales)

@app.route('/sales/new', methods=['GET', 'POST'])
@login_required()
def new_sale():
    """إنشاء فاتورة بيع جديدة"""
    form = SaleForm()
    if form.validate_on_submit():
        try:
            # إنشاء الفاتورة
            sale = Sale(
                customer_id=form.customer_id.data if form.customer_id.data else None,
                total_amount=form.total_amount.data,
                discount=form.discount.data,
                final_amount=form.final_amount.data,
                payment_method=form.payment_method.data,
                notes=form.notes.data
            )
            
            db.session.add(sale)
            db.session.flush()  # للحصول على ID الفاتورة
            
            # إضافة عناصر الفاتورة
            products = request.form.getlist('product_id[]')
            quantities = request.form.getlist('quantity[]')
            unit_prices = request.form.getlist('unit_price[]')
            
            for i, product_id in enumerate(products):
                if product_id and quantities[i] and unit_prices[i]:
                    product = Product.query.get(int(product_id))
                    quantity = int(quantities[i])
                    unit_price = float(unit_prices[i])
                    
                    # التحقق من توفر الكمية
                    if product.quantity < quantity:
                        flash(f'الكمية المطلوبة من {product.name} غير متوفرة', 'error')
                        db.session.rollback()
                        return redirect(url_for('new_sale'))
                    
                    # إنشاء عنصر الفاتورة
                    sale_item = SaleItem(
                        sale_id=sale.id,
                        product_id=int(product_id),
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=quantity * unit_price
                    )
                    
                    # تحديث كمية المنتج
                    product.quantity -= quantity
                    
                    db.session.add(sale_item)
            
            db.session.commit()
            flash('تم إنشاء الفاتورة بنجاح', 'success')
            return redirect(url_for('sales'))
            
        except Exception as e:
            flash(f'خطأ في إنشاء الفاتورة: {str(e)}', 'error')
            db.session.rollback()
    
    customers = Customer.query.all()
    products = Product.query.filter(Product.quantity > 0).all()
    return render_template('new_sale.html', form=form, customers=customers, products=products)

@app.route('/sales/<int:sale_id>')
def view_sale(sale_id):
    """عرض تفاصيل الفاتورة"""
    sale = Sale.query.get_or_404(sale_id)
    return render_template('view_sale.html', sale=sale)

@app.route('/sales/delete/<int:sale_id>', methods=['POST'])
def delete_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    try:
        db.session.delete(sale)
        db.session.commit()
        flash('تم حذف الفاتورة بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف الفاتورة: {e}', 'danger')
    return redirect(url_for('sales'))

# Returns Management Routes
@app.route('/returns')
def returns():
    all_returns = Return.query.all()
    customers = Customer.query.all()
    products = Product.query.all()
    # Prefill sale_id if coming from a sale view
    sale_id_prefill = request.args.get('sale_id', '')
    return render_template('returns.html', returns=all_returns, customers=customers, products=products, sale_id_prefill=sale_id_prefill)

@app.route('/returns/add', methods=['POST'])
@login_required()
def add_return():
    form = ReturnForm()
    if form.validate_on_submit():
        try:
            # Obtener datos del formulario
            sale_id = form.sale_id.data
            customer_id = form.customer_id.data
            total_amount = form.total_amount.data
            reason = form.reason.data
            notes = form.notes.data

            # Validar datos básicos
            if not sale_id:
                return jsonify(success=False, message='رقم الفاتورة الأصلية مطلوب')
            
            # لا نتحقق من إجمالي المدخل؛ سنحسب الإجمالي الفعلي من العناصر لاحقاً

            # Crear objeto de devolución
            new_return = Return(
                sale_id=sale_id,
                customer_id=customer_id if customer_id else None,
                total_amount=total_amount,
                reason=reason,
                notes=notes
            )
            db.session.add(new_return)
            db.session.flush()  # Obtener el ID antes de confirmar

            # Procesar عناصر المرتجع (لا يزال من request.form.getlist لأنها حقول ديناميكية)
            product_ids = request.form.getlist('product_id[]')
            quantities = request.form.getlist('quantity[]')
            prices = request.form.getlist('price[]')

            # Validar que hay al menos un producto
            if not product_ids or len(product_ids) == 0:
                db.session.rollback()
                return jsonify(success=False, message='يجب إضافة منتج واحد على الأقل')

            # Validate sale existence and build sold quantities map
            sale = Sale.query.get(int(sale_id))
            if not sale:
                db.session.rollback()
                return jsonify(success=False, message='رقم الفاتورة الأصلية غير موجود')

            sold_quantities = {}
            for si in sale.sale_items:
                sold_quantities[si.product_id] = sold_quantities.get(si.product_id, 0) + si.quantity

            # Already returned for this sale
            previous_returns = ReturnItem.query.join(Return).filter(Return.sale_id == sale.id).all()
            already_returned = {}
            for ri in previous_returns:
                already_returned[ri.product_id] = already_returned.get(ri.product_id, 0) + ri.quantity

            calculated_total = 0.0

            # Procesar cada elemento con تحقق من الكميات
            for i in range(len(product_ids)):
                if i < len(quantities) and i < len(prices):  # Asegurar que los índices son válidos
                    try:
                        product_id = int(product_ids[i])
                        quantity = int(quantities[i])
                        price = float(prices[i])

                        # Validar datos del producto
                        if not product_id or product_id <= 0:
                            continue  # عناصر غير صالحة
                            
                        if quantity <= 0:
                            continue
                            
                        if price < 0:
                            continue

                        # تحقق وجود المنتج
                        product = Product.query.get(product_id)
                        if not product:
                            continue

                        # تحقق من السماح بالارجاع حسب الفاتورة
                        allowed_qty = sold_quantities.get(product_id, 0) - already_returned.get(product_id, 0)
                        if allowed_qty <= 0:
                            continue  # لم يُبع أو تم إرجاعه بالكامل

                        if quantity > allowed_qty:
                            quantity = allowed_qty  # لا نتجاوز المسموح

                        if quantity <= 0:
                            continue

                        # إنشاء عنصر المرتجع
                        return_item = ReturnItem(
                            return_id=new_return.id,
                            product_id=product_id,
                            quantity=quantity,
                            price=price
                        )
                        db.session.add(return_item)

                        # تحديث المخزون
                        product.quantity += quantity

                        # جمع الإجمالي المحسوب
                        calculated_total += quantity * price
                    except (ValueError, TypeError):
                        continue

            # تحديث الإجمالي المحسوب لضمان التناسق
            new_return.total_amount = calculated_total

            # Confirmar cambios
            db.session.commit()
            # If request expects JSON (AJAX), return JSON; else redirect with flash
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']:
                return jsonify(success=True, message='تم إضافة المرتجع بنجاح!')
            flash('تم إضافة المرتجع بنجاح!', 'success')
            return redirect(url_for('returns'))
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']:
                return jsonify(success=False, message=str(e))
            flash(f'حدث خطأ أثناء إضافة المرتجع: {e}', 'danger')
            return redirect(url_for('returns'))

@app.route('/returns/<int:return_id>')
def view_return(return_id):
    try:
        return_obj = Return.query.get_or_404(return_id)
        return_data = return_obj.to_dict()
        
        # Obtener los elementos de la devolución
        return_items = []
        for item in ReturnItem.query.filter_by(return_id=return_id).all():
            product = Product.query.get(item.product_id)
            product_name = product.name if product else "منتج غير معروف"
            
            return_items.append({
                'id': item.id,
                'product_id': item.product_id,
                'product_name': product_name,
                'quantity': item.quantity,
                'price': item.price,
                'total': item.quantity * item.price
            })
        
        return_data['return_items'] = return_items
        return jsonify(success=True, return_data=return_data)
    except Exception as e:
        return jsonify(success=False, message=str(e))

# API: عناصر الفاتورة القابلة للإرجاع للتعبئة التلقائية
@app.route('/api/sales/<int:sale_id>/returnable-items')
def api_sale_returnable_items(sale_id):
    try:
        sale = Sale.query.get_or_404(sale_id)
        # خريطة الكميات المباعة
        sold = {}
        for si in sale.sale_items:
            sold[si.product_id] = sold.get(si.product_id, 0) + si.quantity
        # خريطة الكميات المرتجعة سابقاً
        prev = {}
        for ri in ReturnItem.query.join(Return).filter(Return.sale_id == sale.id).all():
            prev[ri.product_id] = prev.get(ri.product_id, 0) + ri.quantity
        # بناء العناصر المسموح إرجاعها
        items = []
        for si in sale.sale_items:
            product = si.product
            sold_qty = sold.get(si.product_id, 0)
            returned_qty = prev.get(si.product_id, 0)
            allowed = max(0, sold_qty - returned_qty)
            if allowed > 0:
                items.append({
                    'product_id': si.product_id,
                    'product_name': product.name if product else 'منتج',
                    'sold_qty': sold_qty,
                    'already_returned': returned_qty,
                    'allowed_qty': allowed,
                    'unit_price': si.unit_price
                })
        data = {
            'sale_id': sale.id,
            'customer_id': sale.customer_id,
            'customer_name': sale.customer.name if sale.customer else None,
            'items': items
        }
        return jsonify(success=True, data=data)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 400

@app.route('/returns/delete/<int:return_id>', methods=['POST'])
def delete_return(return_id):
    return_obj = Return.query.get_or_404(return_id)
    try:
        # Before deleting the return, revert stock safely
        for item in return_obj.return_items:
            product = Product.query.get(item.product_id)
            if product:
                product.quantity = max(0, product.quantity - item.quantity)
        db.session.delete(return_obj)
        db.session.commit()
        return jsonify(success=True, message='تم حذف المرتجع بنجاح!')
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=str(e))

# ==================== التقارير ====================

@app.route('/reports')
def reports():
    """صفحة التقارير"""
    # تقرير المبيعات الشهرية
    current_month = datetime.now().replace(day=1)
    monthly_sales = Sale.query.filter(Sale.created_at >= current_month).all()
    monthly_revenue = sum(sale.final_amount for sale in monthly_sales)

    # المرتجعات خلال الشهر وصافي المبيعات
    monthly_returns = Return.query.filter(Return.return_date >= current_month).all()
    monthly_returns_total = sum(r.total_amount for r in monthly_returns)
    net_revenue = monthly_revenue - monthly_returns_total
    
    # تقرير المنتجات الأكثر مبيعاً
    top_products = db.session.query(
        Product.name,
        db.func.sum(SaleItem.quantity).label('total_sold')
    ).join(SaleItem).group_by(Product.id).order_by(
        db.func.sum(SaleItem.quantity).desc()
    ).limit(10).all()
    
    # تقرير المخزون المنخفض
    low_stock = Product.query.filter(
        Product.quantity <= Product.min_quantity
    ).all()
    
    return render_template('reports.html',
                         monthly_revenue=monthly_revenue,
                         monthly_sales_count=len(monthly_sales),
                         top_products=top_products,
                         low_stock=low_stock,
                         monthly_returns_total=monthly_returns_total,
                         net_revenue=net_revenue)

# ==================== API للتكامل مع n8n/Google Sheets ====================

@app.route('/api/reports/sales.json')
def api_reports_sales_json():
    """تقرير المبيعات كـ JSON للتكامل الخارجي (n8n/Google Sheets)"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Sale.query
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(Sale.created_at >= start_date)
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        query = query.filter(Sale.created_at <= end_date)

    sales = query.order_by(Sale.created_at.desc()).all()
    return jsonify([s.to_dict() for s in sales])

# ==================== API للبحث ====================

@app.route('/api/products/search')
def api_search_products():
    """البحث عن المنتجات عبر API - محسن"""
    query = request.args.get('q', '')
    
    if query:
        # بحث محسن يدعم البحث الجزئي والمرن
        search_terms = query.split()
        products_query = Product.query
        
        for term in search_terms:
            products_query = products_query.filter(
                db.or_(
                    Product.name.ilike(f'%{term}%'),
                    Product.brand.ilike(f'%{term}%'),
                    Product.model.ilike(f'%{term}%'),
                    Product.description.ilike(f'%{term}%'),
                    Product.barcode.ilike(f'%{term}%')
                )
            )
        
        products = products_query.limit(10).all()
    else:
        products = Product.query.limit(10).all()
    
    return jsonify([product.to_dict() for product in products])

@app.route('/api/customers/search')
def api_search_customers():
    """البحث عن العملاء عبر API"""
    query = request.args.get('q', '')
    
    if query:
        customers = Customer.query.filter(
            db.or_(
                Customer.name.contains(query),
                Customer.phone.contains(query)
            )
        ).limit(10).all()
    else:
        customers = Customer.query.limit(10).all()
    
    return jsonify([customer.to_dict() for customer in customers])

# ==================== فواتير الموردين ====================

@app.route('/purchases')
def purchases():
    """صفحة فواتير الشراء"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    purchases = PurchaseInvoice.query.order_by(PurchaseInvoice.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('purchases.html', purchases=purchases)

@app.route('/purchases/new', methods=['GET', 'POST'])
def new_purchase():
    """إنشاء فاتورة شراء جديدة"""
    if request.method == 'POST':
        try:
            # إنشاء رقم فاتورة تلقائي
            last_invoice = PurchaseInvoice.query.order_by(PurchaseInvoice.id.desc()).first()
            invoice_number = f"PUR-{(last_invoice.id + 1) if last_invoice else 1:06d}"
            
            # إنشاء الفاتورة
            purchase = PurchaseInvoice(
                supplier_id=int(request.form['supplier_id']),
                invoice_number=invoice_number,
                total_amount=float(request.form['total_amount']),
                discount=float(request.form.get('discount', 0)),
                final_amount=float(request.form['final_amount']),
                payment_method=request.form.get('payment_method', 'نقدي'),
                notes=request.form.get('notes', '')
            )
            
            db.session.add(purchase)
            db.session.flush()  # للحصول على ID الفاتورة
            
            # إضافة عناصر الفاتورة وتحديث المخزون
            products = request.form.getlist('product_id[]')
            quantities = request.form.getlist('quantity[]')
            unit_prices = request.form.getlist('unit_price[]')
            
            for i, product_id in enumerate(products):
                if product_id and quantities[i] and unit_prices[i]:
                    product = Product.query.get(int(product_id))
                    quantity = int(quantities[i])
                    unit_price = float(unit_prices[i])
                    
                    # إنشاء عنصر الفاتورة
                    purchase_item = PurchaseItem(
                        purchase_invoice_id=purchase.id,
                        product_id=int(product_id),
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=quantity * unit_price
                    )
                    
                    # تحديث كمية المنتج (إضافة للمخزون)
                    product.quantity += quantity
                    # تحديث سعر الشراء
                    product.price_buy = unit_price
                    
                    db.session.add(purchase_item)
            
            db.session.commit()
            flash('تم إنشاء فاتورة الشراء بنجاح وتم تحديث المخزون', 'success')
            return redirect(url_for('purchases'))
            
        except Exception as e:
            flash(f'خطأ في إنشاء فاتورة الشراء: {str(e)}', 'error')
            db.session.rollback()
    
    suppliers = Supplier.query.all()
    products = Product.query.all()
    return render_template('new_purchase.html', suppliers=suppliers, products=products)

@app.route('/purchases/<int:purchase_id>')
def view_purchase(purchase_id):
    """عرض تفاصيل فاتورة الشراء"""
    purchase = PurchaseInvoice.query.get_or_404(purchase_id)
    return render_template('view_purchase.html', purchase=purchase)

# ==================== تصدير الفواتير (PDF عادي) ====================

@app.route('/sales/<int:sale_id>/regular-pdf')
def sale_regular_pdf(sale_id):
    """تصدير فاتورة البيع كـ PDF عادي (A4)"""
    sale = Sale.query.get_or_404(sale_id)
    
    # إنشاء فاتورة A4 عادية
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, 
                           topMargin=20*mm, bottomMargin=20*mm)
    
    styles = getSampleStyleSheet()
    story = []
    
    # عنوان الفاتورة
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], 
                                fontSize=18, spaceAfter=12, alignment=TA_CENTER)
    story.append(Paragraph("فاتورة بيع", title_style))
    story.append(Spacer(1, 10*mm))
    
    # معلومات الفاتورة
    info_style = ParagraphStyle('Info', parent=styles['Normal'], 
                               fontSize=12, spaceAfter=6, alignment=TA_RIGHT)
    
    story.append(Paragraph(f"رقم الفاتورة: {convert_to_english_numbers_app(str(sale.id))}", info_style))
    story.append(Paragraph(f"التاريخ: {convert_to_english_numbers_app(sale.created_at.strftime('%Y-%m-%d'))}", info_style))
    story.append(Paragraph(f"الوقت: {convert_to_english_numbers_app(sale.created_at.strftime('%H:%M'))}", info_style))
    
    if sale.customer:
        story.append(Paragraph(f"العميل: {sale.customer.name}", info_style))
        if sale.customer.phone:
            story.append(Paragraph(f"الهاتف: {convert_to_english_numbers_app(sale.customer.phone)}", info_style))
    
    story.append(Spacer(1, 10*mm))
    
    # جدول المنتجات
    table_data = [['المنتج', 'الكمية', 'سعر الوحدة', 'المجموع']]
    
    for item in sale.sale_items:
        table_data.append([
            item.product.name,
            convert_to_english_numbers_app(str(item.quantity)),
            currency_filter(item.unit_price),
            currency_filter(item.total_price)
        ])
    
    table = Table(table_data, colWidths=[80*mm, 30*mm, 40*mm, 40*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 10*mm))
    
    # المجاميع
    totals_style = ParagraphStyle('Totals', parent=styles['Normal'], 
                                 fontSize=12, spaceAfter=6, alignment=TA_RIGHT)
    
    story.append(Paragraph(f"المجموع الفرعي: {currency_filter(sale.total_amount)}", totals_style))
    if sale.discount > 0:
        story.append(Paragraph(f"الخصم: {currency_filter(sale.discount)}", totals_style))
    
    final_style = ParagraphStyle('Final', parent=styles['Normal'], 
                                fontSize=14, spaceAfter=6, alignment=TA_RIGHT, 
                                textColor=colors.red)
    story.append(Paragraph(f"المجموع النهائي: {currency_filter(sale.final_amount)}", final_style))
    
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(f"طريقة الدفع: {sale.payment_method}", info_style))
    
    if sale.notes:
        story.append(Spacer(1, 5*mm))
        story.append(Paragraph(f"ملاحظات: {sale.notes}", info_style))
    
    doc.build(story)
    buffer.seek(0)
    
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=regular_sale_{sale_id}.pdf'
    
    return response

@app.route('/purchases/<int:purchase_id>/regular-pdf')
def purchase_regular_pdf(purchase_id):
    """تصدير فاتورة الشراء كـ PDF عادي (A4)"""
    purchase = PurchaseInvoice.query.get_or_404(purchase_id)
    
    # إنشاء فاتورة A4 عادية
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, 
                           topMargin=20*mm, bottomMargin=20*mm)
    
    styles = getSampleStyleSheet()
    story = []
    
    # عنوان الفاتورة
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], 
                                fontSize=18, spaceAfter=12, alignment=TA_CENTER)
    story.append(Paragraph("فاتورة شراء", title_style))
    story.append(Spacer(1, 10*mm))
    
    # معلومات الفاتورة
    info_style = ParagraphStyle('Info', parent=styles['Normal'], 
                               fontSize=12, spaceAfter=6, alignment=TA_RIGHT)
    
    story.append(Paragraph(f"رقم الفاتورة: {convert_to_english_numbers_app(purchase.invoice_number)}", info_style))
    story.append(Paragraph(f"التاريخ: {convert_to_english_numbers_app(purchase.created_at.strftime('%Y-%m-%d'))}", info_style))
    story.append(Paragraph(f"الوقت: {convert_to_english_numbers_app(purchase.created_at.strftime('%H:%M'))}", info_style))
    
    story.append(Paragraph(f"المورد: {purchase.supplier.name}", info_style))
    if purchase.supplier.company:
        story.append(Paragraph(f"الشركة: {purchase.supplier.company}", info_style))
    if purchase.supplier.phone:
        story.append(Paragraph(f"الهاتف: {convert_to_english_numbers_app(purchase.supplier.phone)}", info_style))
    
    story.append(Spacer(1, 10*mm))
    
    # جدول المنتجات
    table_data = [['المنتج', 'الكمية', 'سعر الوحدة', 'المجموع']]
    
    for item in purchase.purchase_items:
        table_data.append([
            item.product.name,
            convert_to_english_numbers_app(str(item.quantity)),
            currency_filter(item.unit_price),
            currency_filter(item.total_price)
        ])
    
    table = Table(table_data, colWidths=[80*mm, 30*mm, 40*mm, 40*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 10*mm))
    
    # المجاميع
    totals_style = ParagraphStyle('Totals', parent=styles['Normal'], 
                                 fontSize=12, spaceAfter=6, alignment=TA_RIGHT)
    
    story.append(Paragraph(f"المجموع الفرعي: {currency_filter(purchase.total_amount)}", totals_style))
    if purchase.discount > 0:
        story.append(Paragraph(f"الخصم: {currency_filter(purchase.discount)}", totals_style))
    
    final_style = ParagraphStyle('Final', parent=styles['Normal'], 
                                fontSize=14, spaceAfter=6, alignment=TA_RIGHT, 
                                textColor=colors.red)
    story.append(Paragraph(f"المجموع النهائي: {currency_filter(purchase.final_amount)}", final_style))
    
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(f"طريقة الدفع: {purchase.payment_method}", info_style))
    
    if purchase.notes:
        story.append(Spacer(1, 5*mm))
        story.append(Paragraph(f"ملاحظات: {purchase.notes}", info_style))
    
    doc.build(story)
    buffer.seek(0)
    
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=regular_purchase_{purchase_id}.pdf'
    
    return response

# ==================== تصدير Excel ====================

@app.route('/reports/sales/excel')
def export_sales_excel():
    """تصدير تقرير المبيعات إلى Excel"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Sale.query
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(Sale.created_at >= start_date)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        query = query.filter(Sale.created_at <= end_date)
    
    sales = query.order_by(Sale.created_at.desc()).all()
    
    # تصدير إلى Excel
    exporter = ExcelExporter()
    excel_data = exporter.export_sales_report(sales, start_date, end_date)
    
    # إنشاء response
    response = make_response(excel_data)
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = 'attachment; filename=sales_report.xlsx'
    
    return response

@app.route('/reports/products/excel')
def export_products_excel():
    """تصدير تقرير المنتجات إلى Excel"""
    products = Product.query.order_by(Product.name).all()
    
    # تصدير إلى Excel
    exporter = ExcelExporter()
    excel_data = exporter.export_products_report(products)
    
    # إنشاء response
    response = make_response(excel_data)
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = 'attachment; filename=products_report.xlsx'
    
    return response

@app.route('/reports/purchases/excel')
def export_purchases_excel():
    """تصدير تقرير المشتريات إلى Excel"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = PurchaseInvoice.query
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(PurchaseInvoice.created_at >= start_date)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        query = query.filter(PurchaseInvoice.created_at <= end_date)
    
    purchases = query.order_by(PurchaseInvoice.created_at.desc()).all()
    
    # تصدير إلى Excel
    exporter = ExcelExporter()
    excel_data = exporter.export_purchases_report(purchases, start_date, end_date)
    
    # إنشاء response
    response = make_response(excel_data)
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = 'attachment; filename=purchases_report.xlsx'
    
    return response

# ==================== تحسين التقارير ====================

@app.route('/reports/advanced')
def advanced_reports():
    """صفحة التقارير المتقدمة"""
    # تقرير المبيعات حسب الفترة
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    sales_query = Sale.query
    purchases_query = PurchaseInvoice.query
    
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        sales_query = sales_query.filter(Sale.created_at >= start_date_obj)
        purchases_query = purchases_query.filter(PurchaseInvoice.created_at >= start_date_obj)
    
    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        sales_query = sales_query.filter(Sale.created_at <= end_date_obj)
        purchases_query = purchases_query.filter(PurchaseInvoice.created_at <= end_date_obj)
    
    sales = sales_query.all()
    purchases = purchases_query.all()
    
    # حساب الإحصائيات
    total_sales_revenue = sum(sale.final_amount for sale in sales)
    total_purchases_cost = sum(purchase.final_amount for purchase in purchases)
    profit = total_sales_revenue - total_purchases_cost
    
    # أكثر المنتجات مبيعاً
    top_products = db.session.query(
        Product.name,
        Product.brand,
        db.func.sum(SaleItem.quantity).label('total_sold'),
        db.func.sum(SaleItem.total_price).label('total_revenue')
    ).join(SaleItem).group_by(Product.id).order_by(
        db.func.sum(SaleItem.quantity).desc()
    ).limit(10).all()
    
    # المنتجات منخفضة المخزون
    low_stock = Product.query.filter(
        Product.quantity <= Product.min_quantity
    ).all()
    
    return render_template('advanced_reports.html',
                         sales=sales,
                         purchases=purchases,
                         total_sales_revenue=total_sales_revenue,
                         total_purchases_cost=total_purchases_cost,
                         profit=profit,
                         top_products=top_products,
                         low_stock=low_stock,
                         start_date=start_date,
                         end_date=end_date)

# ==================== صفحة إعدادات المتجر ====================

@app.route('/settings', methods=['GET', 'POST'])
def settings_page():
    settings = StoreSettings.query.first()
    if request.method == 'POST':
        try:
            settings.store_name = request.form.get('store_name', settings.store_name)
            settings.store_name_ar = request.form.get('store_name_ar', settings.store_name_ar)
            settings.address = request.form.get('address', settings.address)
            settings.phone = request.form.get('phone', settings.phone)
            settings.email = request.form.get('email', settings.email)
            settings.currency_name = request.form.get('currency_name', settings.currency_name)
            settings.currency_symbol = request.form.get('currency_symbol', settings.currency_symbol)
            db.session.commit()
            flash('تم تحديث إعدادات المتجر بنجاح', 'success')
            return redirect(url_for('settings_page'))
        except Exception as e:
            db.session.rollback()
            flash(f'خطأ في تحديث الإعدادات: {str(e)}', 'error')
    return render_template('settings.html', settings=settings)

# ==================== مساعد تنسيق العملة ====================

def convert_to_english_numbers_app(text):
    """تحويل الأرقام العربية إلى إنجليزية في التطبيق"""
    if text is None:
        return ""
    
    arabic_to_english = {
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
    }
    
    text = str(text)
    for arabic, english in arabic_to_english.items():
        text = text.replace(arabic, english)
    
    return text

@app.template_filter('currency')
def currency_filter(amount):
    """فلتر تنسيق العملة بأرقام إنجليزية اعتماداً على إعدادات المتجر"""
    if amount is None:
        return "0"
    formatted = f"{amount:,.0f}"
    formatted = convert_to_english_numbers_app(formatted)
    settings = None
    try:
        settings = StoreSettings.query.first()
    except Exception:
        pass
    symbol = settings.currency_symbol if settings and settings.currency_symbol else 'د.ج'
    return f"{formatted} {symbol}"

@app.template_filter('currency_decimal')
def currency_decimal_filter(amount):
    """فلتر تنسيق العملة مع الكسور العشرية بأرقام إنجليزية"""
    if amount is None:
        return "0.00"
    formatted = f"{amount:,.2f}"
    formatted = convert_to_english_numbers_app(formatted)
    settings = None
    try:
        settings = StoreSettings.query.first()
    except Exception:
        pass
    symbol = settings.currency_symbol if settings and settings.currency_symbol else 'د.ج'
    return f"{formatted} {symbol}"

@app.template_filter('english_numbers')
def english_numbers_filter(text):
    """فلتر تحويل الأرقام العربية إلى إنجليزية"""
    return convert_to_english_numbers_app(text)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Check if default settings exist, if not, create them
        if not StoreSettings.query.first():
            # Add default settings if they don't exist
            default_settings = StoreSettings(store_name="My Phone Store", currency="USD")
            db.session.add(default_settings)
            db.session.commit()
    app.run(debug=True, host='127.0.0.1', port=5000)
# تعليق جديد لتشغيل نشر جديد على Render

