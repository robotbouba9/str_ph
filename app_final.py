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

# جلسات للمصادقة
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import session

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

# الصفحة الرئيسية
@app.route('/')
@login_required()
def index():
    return render_template('index.html')

# صفحة المنتجات
@app.route('/products')
@login_required(role='inventory')
def products():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    products = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('products.html', products=products)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required(role='inventory')
def add_product():
    form = ProductForm()
    categories = Category.query.all()
    brands = Brand.query.all()
    suppliers = Supplier.query.all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    form.brand_id.choices = [(b.id, b.name) for b in brands]
    form.supplier_id.choices = [(s.id, s.name) for s in suppliers]
    return render_template('add_product.html', form=form, categories=categories, brands=brands, suppliers=suppliers)

@app.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required(role='inventory')
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

        product.name = form.name.data
        product.description = form.description.data
        product.category_id = form.category_id.data
        product.brand_id = form.brand_id.data
        product.supplier_id = form.supplier_id.data
        product.price = form.price.data
        product.cost_price = form.cost_price.data
        product.quantity = form.quantity.data
        product.barcode = form.barcode.data
        product.imei = form.imei.data
        product.warranty_period = form.warranty_period.data
        product.unit = form.unit.data
        product.notes = form.notes.data

        db.session.commit()
        flash('تم تحديث المنتج بنجاح', 'success')
        return redirect(url_for('products'))

    categories = Category.query.all()
    brands = Brand.query.all()
    suppliers = Supplier.query.all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    form.brand_id.choices = [(b.id, b.name) for b in brands]
    form.supplier_id.choices = [(s.id, s.name) for s in suppliers]
    return render_template('edit_product.html', form=form, product=product, categories=categories, brands=brands, suppliers=suppliers)

@app.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required(role='admin')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash('تم حذف المنتج بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف المنتج: {e}', 'danger')
    return redirect(url_for('products'))

# صفحة المبيعات
@app.route('/sales')
@login_required(role='cashier')
def sales():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    sales = Sale.query.order_by(Sale.sale_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('sales.html', sales=sales)

@app.route('/sales/new', methods=['GET', 'POST'])
@login_required(role='cashier')
def new_sale():
    form = SaleForm()

    if form.validate_on_submit():
        try:
            # إنشاء فاتورة جديدة
            sale = Sale(
                customer_id=form.customer_id.data,
                sale_date=datetime.now(),
                user_id=session.get('user_id'),
                payment_method=form.payment_method.data,
                notes=form.notes.data
            )

            db.session.add(sale)
            db.session.flush()  # للحصول على sale.id

            # معالجة بنود البيع
            total_amount = 0
            for item in form.items:
                product = Product.query.get(item.product_id.data)
                if product:
                    quantity = item.quantity.data
                    unit_price = item.unit_price.data
                    total_price = quantity * unit_price

                    # إنشاء بند البيع
                    sale_item = SaleItem(
                        sale_id=sale.id,
                        product_id=item.product_id.data,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=total_price
                    )

                    db.session.add(sale_item)

                    # تحديث كمية المنتج
                    product.quantity -= quantity

                    total_amount += total_price

            sale.total_amount = total_amount
            sale.paid_amount = form.paid_amount.data
            sale.balance = total_amount - form.paid_amount.data

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
@login_required(role='cashier')
def view_sale(sale_id):
    """عرض تفاصيل الفاتورة"""
    sale = Sale.query.get_or_404(sale_id)
    return render_template('view_sale.html', sale=sale)

@app.route('/sales/delete/<int:sale_id>', methods=['POST'])
@login_required(role='admin')
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
@login_required(role='cashier')
def returns():
    all_returns = Return.query.all()
    customers = Customer.query.all()
    products = Product.query.all()
    # Prefill sale_id if coming from a sale view
    sale_id_prefill = request.args.get('sale_id', '')
    return render_template('returns.html', returns=all_returns, customers=customers, products=products, sale_id_prefill=sale_id_prefill)

@app.route('/returns/add', methods=['POST'])
@login_required(role='cashier')
def add_return():
    form = ReturnForm()
    if form.validate_on_submit():
        try:
            # إنشاء سجل الإرجاع
            return_item = Return(
                sale_id=form.sale_id.data,
                customer_id=form.customer_id.data,
                product_id=form.product_id.data,
                quantity=form.quantity.data,
                return_date=datetime.now(),
                reason=form.reason.data,
                user_id=session.get('user_id')
            )

            db.session.add(return_item)
            db.session.commit()

            flash('تم تسجيل الإرجاع بنجاح', 'success')
            return redirect(url_for('returns'))

        except Exception as e:
            flash(f'خطأ في تسجيل الإرجاع: {str(e)}', 'error')
            db.session.rollback()

    return redirect(url_for('returns'))

# صفحة العملاء
@app.route('/customers')
@login_required(role='inventory')
def customers():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    customers = Customer.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('customers.html', customers=customers)

@app.route('/customers/add', methods=['GET', 'POST'])
@login_required(role='inventory')
def add_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(
            name=form.name.data,
            phone=form.phone.data,
            address=form.address.data,
            notes=form.notes.data
        )
        db.session.add(customer)
        db.session.commit()
        flash('تم إضافة العميل بنجاح', 'success')
        return redirect(url_for('customers'))
    return render_template('add_customer.html', form=form)

@app.route('/customers/edit/<int:customer_id>', methods=['GET', 'POST'])
@login_required(role='inventory')
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    form = CustomerForm(obj=customer)
    if form.validate_on_submit():
        customer.name = form.name.data
        customer.phone = form.phone.data
        customer.address = form.address.data
        customer.notes = form.notes.data
        db.session.commit()
        flash('تم تحديث العميل بنجاح', 'success')
        return redirect(url_for('customers'))
    return render_template('edit_customer.html', form=form, customer=customer)

@app.route('/customers/delete/<int:customer_id>', methods=['POST'])
@login_required(role='admin')
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    try:
        db.session.delete(customer)
        db.session.commit()
        flash('تم حذف العميل بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف العميل: {e}', 'danger')
    return redirect(url_for('customers'))

# صفحة الموردين
@app.route('/suppliers')
@login_required(role='inventory')
def suppliers():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    suppliers = Supplier.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('suppliers.html', suppliers=suppliers)

@app.route('/suppliers/add', methods=['GET', 'POST'])
@login_required(role='inventory')
def add_supplier():
    form = SupplierForm()
    if form.validate_on_submit():
        supplier = Supplier(
            name=form.name.data,
            phone=form.phone.data,
            address=form.address.data,
            notes=form.notes.data
        )
        db.session.add(supplier)
        db.session.commit()
        flash('تم إضافة المورد بنجاح', 'success')
        return redirect(url_for('suppliers'))
    return render_template('add_supplier.html', form=form)

@app.route('/suppliers/edit/<int:supplier_id>', methods=['GET', 'POST'])
@login_required(role='inventory')
def edit_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    form = SupplierForm(obj=supplier)
    if form.validate_on_submit():
        supplier.name = form.name.data
        supplier.phone = form.phone.data
        supplier.address = form.address.data
        supplier.notes = form.notes.data
        db.session.commit()
        flash('تم تحديث المورد بنجاح', 'success')
        return redirect(url_for('suppliers'))
    return render_template('edit_supplier.html', form=form, supplier=supplier)

@app.route('/suppliers/delete/<int:supplier_id>', methods=['POST'])
@login_required(role='admin')
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    try:
        db.session.delete(supplier)
        db.session.commit()
        flash('تم حذف المورد بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف المورد: {e}', 'danger')
    return redirect(url_for('suppliers'))

# صفحة الفئات
@app.route('/categories')
@login_required(role='inventory')
def categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/categories/add', methods=['POST'])
@login_required(role='inventory')
def add_category():
    name = request.form.get('name')
    if name:
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('تم إضافة الفئة بنجاح', 'success')
    return redirect(url_for('categories'))

@app.route('/categories/delete/<int:category_id>', methods=['POST'])
@login_required(role='admin')
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    try:
        db.session.delete(category)
        db.session.commit()
        flash('تم حذف الفئة بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف الفئة: {e}', 'danger')
    return redirect(url_for('categories'))

# صفحة العلامات التجارية
@app.route('/brands')
@login_required(role='inventory')
def brands():
    brands = Brand.query.all()
    return render_template('brands.html', brands=brands)

@app.route('/brands/add', methods=['POST'])
@login_required(role='inventory')
def add_brand():
    name = request.form.get('name')
    if name:
        brand = Brand(name=name)
        db.session.add(brand)
        db.session.commit()
        flash('تم إضافة العلامة التجارية بنجاح', 'success')
    return redirect(url_for('brands'))

@app.route('/brands/delete/<int:brand_id>', methods=['POST'])
@login_required(role='admin')
def delete_brand(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    try:
        db.session.delete(brand)
        db.session.commit()
        flash('تم حذف العلامة التجارية بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف العلامة التجارية: {e}', 'danger')
    return redirect(url_for('brands'))

# صفحة الإعدادات
@app.route('/settings')
@login_required(role='admin')
def settings():
    settings = StoreSettings.query.first()
    if not settings:
        settings = StoreSettings()
        db.session.add(settings)
        db.session.commit()
    form = StoreSettingsForm(obj=settings)
    return render_template('settings.html', form=form)

@app.route('/settings/save', methods=['POST'])
@login_required(role='admin')
def save_settings():
    settings = StoreSettings.query.first()
    form = StoreSettingsForm(request.form, obj=settings)
    if form.validate():
        settings.store_name = form.store_name.data
        settings.address = form.address.data
        settings.phone = form.phone.data
        settings.email = form.email.data
        settings.tax_rate = form.tax_rate.data
        settings.currency = form.currency.data
        settings.currency_symbol = form.currency_symbol.data
        settings.invoice_footer = form.invoice_footer.data
        db.session.commit()
        flash('تم حفظ الإعدادات بنجاح', 'success')
        return redirect(url_for('settings'))
    return render_template('settings.html', form=form)

# صفحة المستخدمين
@app.route('/users')
@login_required(role='admin')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/users/add', methods=['GET', 'POST'])
@login_required(role='admin')
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            password_hash=generate_password_hash(form.password.data),
            role=form.role.data,
            is_active=form.is_active.data
        )
        db.session.add(user)
        db.session.commit()
        flash('تم إضافة المستخدم بنجاح', 'success')
        return redirect(url_for('users'))
    return render_template('add_user.html', form=form)

@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required(role='admin')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.role = form.role.data
        user.is_active = form.is_active.data
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        flash('تم تحديث المستخدم بنجاح', 'success')
        return redirect(url_for('users'))
    return render_template('edit_user.html', form=form, user=user)

@app.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required(role='admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('تم حذف المستخدم بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف المستخدم: {e}', 'danger')
    return redirect(url_for('users'))

# صفحة فواتير الشراء
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

@app.route('/purchases/<int:purchase_id>/regular-pdf')
def purchase_pdf(purchase_id):
    """إنشاء PDF عادي لفاتورة الشراء"""
    purchase = PurchaseInvoice.query.get_or_404(purchase_id)
    return render_template('purchase_pdf.html', purchase=purchase)

@app.route('/reports/purchases/excel')
def export_purchases():
    """تصدير فواتير الشراء إلى Excel"""
    purchases = PurchaseInvoice.query.order_by(PurchaseInvoice.created_at.desc()).all()

    exporter = ExcelExporter()
    output = exporter.export_purchases(purchases)

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=purchases.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response

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

@app.route('/purchases/<int:purchase_id>')
def view_purchase(purchase_id):
    """عرض تفاصيل فاتورة الشراء"""
    purchase = PurchaseInvoice.query.get_or_404(purchase_id)
    return render_template('view_purchase.html', purchase=purchase)

@app.route('/purchases/<int:purchase_id>/regular-pdf')
def purchase_pdf(purchase_id):
    """إنشاء PDF عادي لفاتورة الشراء"""
    purchase = PurchaseInvoice.query.get_or_404(purchase_id)
    return render_template('purchase_pdf.html', purchase=purchase)

@app.route('/reports/purchases/excel')
def export_purchases():
    """تصدير فواتير الشراء إلى Excel"""
    purchases = PurchaseInvoice.query.order_by(PurchaseInvoice.created_at.desc()).all()

    exporter = ExcelExporter()
    output = exporter.export_purchases(purchases)

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=purchases.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response

# صفحة التقارير
@app.route('/reports')
@login_required(role='admin')
def reports():
    return render_template('reports.html')

@app.route('/reports/sales')
@login_required(role='admin')
def sales_reports():
    start_date = request.args.get('start_date', datetime.now().strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

    sales = Sale.query.filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ).order_by(Sale.sale_date.desc()).all()

    return render_template('sales_reports.html', sales=sales, start_date=start_date, end_date=end_date)

@app.route('/reports/products')
@login_required(role='admin')
def products_reports():
    products = Product.query.all()
    return render_template('products_reports.html', products=products)

@app.route('/reports/export/sales')
@login_required(role='admin')
def export_sales():
    start_date = request.args.get('start_date', datetime.now().strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

    sales = Sale.query.filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ).order_by(Sale.sale_date.desc()).all()

    exporter = ExcelExporter()
    output = exporter.export_sales(sales)

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename=t sales_{start_date}_to_{end_date}.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response

@app.route('/reports/export/products')
@login_required(role='admin')
def export_products():
    products = Product.query.all()

    exporter = ExcelExporter()
    output = exporter.export_products(products)

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=products.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response

# مساعدات
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def secure_filename(filename):
    import re
    import unicodedata
    filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    filename = re.sub(r'[^\w\s-]', '', filename).strip()
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename

# فلتر لتحويل الأرقام العربية إلى إنجليزية
def convert_to_english_numbers_app(text):
    """تحويل الأرقام العربية إلى إنجليزية"""
    arabic_to_english = {
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
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

# إضافة نموذج فاتورة البيع
from forms import SaleForm, SaleItemForm

# إضافة مسار للبحث عن العملاء
@app.route('/api/customers/search')
def search_customers():
    query = request.args.get('query', '')
    if query:
        customers = Customer.query.filter(
            Customer.name.contains(query) | Customer.phone.contains(query)
        ).limit(10).all()
    else:
        customers = Customer.query.limit(10).all()

    return jsonify([customer.to_dict() for customer in customers])

# إضافة مسار للبحث عن المنتجات
@app.route('/api/products/search')
def search_products():
    query = request.args.get('query', '')
    if query:
        products = Product.query.filter(
            Product.name.contains(query) | Product.barcode.contains(query) | Product.imei.contains(query)
        ).limit(20).all()
    else:
        products = Product.query.filter(Product.quantity > 0).limit(20).all()

    return jsonify([{
        'id': p.id,
        'name': p.name,
        'quantity': p.quantity,
        'price': p.price,
        'barcode': p.barcode,
        'imei': p.imei
    } for p in products])

# إضافة مسار للحصول على تفاصيل المنتج
@app.route('/api/products/<int:product_id>')
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

# إضافة مسار للحصول على تفاصيل العميل
@app.route('/api/customers/<int:customer_id>')
def get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return jsonify(customer.to_dict())

if __name__ == '__main__':
    app.run(debug=True)
