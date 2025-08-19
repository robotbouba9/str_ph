# -*- coding: utf-8 -*-
"""
تطبيق Flask لإدارة مخزون محل الهواتف - نسخة تعمل بكامل وظائفها
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
    if request.method == 'POST':
        try:
            # إنشاء فاتورة جديدة
            sale = Sale(
                customer_id=int(request.form['customer_id']),
                sale_date=datetime.now(),
                user_id=session.get('user_id'),
                payment_method=request.form.get('payment_method', 'نقدي'),
                notes=request.form.get('notes', '')
            )

            db.session.add(sale)
            db.session.flush()  # للحصول على sale.id

            # معالجة بنود البيع
            products = request.form.getlist('product_id[]')
            quantities = request.form.getlist('quantity[]')
            unit_prices = request.form.getlist('unit_price[]')

            total_amount = 0
            for i, product_id in enumerate(products):
                if product_id and quantities[i] and unit_prices[i]:
                    product = Product.query.get(int(product_id))
                    quantity = int(quantities[i])
                    unit_price = float(unit_prices[i])
                    total_price = quantity * unit_price

                    # إنشاء بند البيع
                    sale_item = SaleItem(
                        sale_id=sale.id,
                        product_id=int(product_id),
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=total_price
                    )

                    db.session.add(sale_item)

                    # تحديث كمية المنتج
                    product.quantity -= quantity

                    total_amount += total_price

            sale.total_amount = total_amount
            sale.paid_amount = float(request.form['paid_amount'])
            sale.balance = total_amount - float(request.form['paid_amount'])

            db.session.commit()
            flash('تم إنشاء الفاتورة بنجاح', 'success')
            return redirect(url_for('sales'))

        except Exception as e:
            flash(f'خطأ في إنشاء الفاتورة: {str(e)}', 'error')
            db.session.rollback()

    customers = Customer.query.all()
    products = Product.query.filter(Product.quantity > 0).all()
    return render_template('new_sale.html', customers=customers, products=products)

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
            email=form.email.data,
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
        customer.email = form.email.data
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
            email=form.email.data,
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
        supplier.email = form.email.data
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

# تشغيل التطبيق
if __name__ == '__main__':
    print("🚀 بدء تشغيل تطبيق الويب...")
    print("🌐 يمكنك الوصول للتطبيق على: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
