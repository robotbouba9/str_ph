# -*- coding: utf-8 -*-
"""
تطبيق Flask لإدارة مخزون محل الهواتف
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, make_response, send_file
from database import db, init_database, Product, Customer, Supplier, Sale, SaleItem, Category, PurchaseInvoice, PurchaseItem, StoreSettings
from datetime import datetime, timedelta
from excel_export import ExcelExporter
from dotenv import load_dotenv
import os
from io import BytesIO

# إعداد التطبيق
load_dotenv()
app = Flask(__name__)

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

@app.route('/')
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

# ==================== إدارة المنتجات ====================

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
    brands = db.session.query(Product.brand).distinct().all()
    brands = [brand[0] for brand in brands if brand[0]]
    categories = Category.query.all()
    
    return render_template('products.html', products=products, brands=brands, categories=categories)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    """إضافة منتج جديد"""
    if request.method == 'POST':
        try:
            product = Product(
                name=request.form['name'],
                brand=request.form['brand'],
                model=request.form['model'],
                color=request.form.get('color', ''),
                description=request.form.get('description', ''),
                price_buy=float(request.form['price_buy']),
                price_sell=float(request.form['price_sell']),
                quantity=int(request.form['quantity']),
                min_quantity=int(request.form.get('min_quantity', 5)),
                barcode=request.form.get('barcode', ''),
                category_id=int(request.form['category_id']) if request.form['category_id'] else None,
                supplier_id=int(request.form['supplier_id']) if request.form['supplier_id'] else None
            )
            
            db.session.add(product)
            db.session.commit()
            flash('تم إضافة المنتج بنجاح', 'success')
            return redirect(url_for('products'))
            
        except Exception as e:
            flash(f'خطأ في إضافة المنتج: {str(e)}', 'error')
            db.session.rollback()
    
    suppliers = Supplier.query.all()
    categories = Category.query.all()
    return render_template('add_product.html', suppliers=suppliers, categories=categories)

@app.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    """تعديل منتج"""
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        try:
            product.name = request.form['name']
            product.brand = request.form['brand']
            product.model = request.form['model']
            product.color = request.form.get('color', '')
            product.description = request.form.get('description', '')
            product.price_buy = float(request.form['price_buy'])
            product.price_sell = float(request.form['price_sell'])
            product.quantity = int(request.form['quantity'])
            product.min_quantity = int(request.form.get('min_quantity', 5))
            product.barcode = request.form.get('barcode', '')
            product.category_id = int(request.form['category_id']) if request.form['category_id'] else None
            product.supplier_id = int(request.form['supplier_id']) if request.form['supplier_id'] else None
            product.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('تم تحديث المنتج بنجاح', 'success')
            return redirect(url_for('products'))
            
        except Exception as e:
            flash(f'خطأ في تحديث المنتج: {str(e)}', 'error')
            db.session.rollback()
    
    suppliers = Supplier.query.all()
    categories = Category.query.all()
    return render_template('edit_product.html', product=product, suppliers=suppliers, categories=categories)

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
def add_category():
    """إضافة فئة جديدة"""
    if request.method == 'POST':
        try:
            category = Category(
                name=request.form['name'],
                description=request.form.get('description', '')
            )
            
            db.session.add(category)
            db.session.commit()
            flash('تم إضافة الفئة بنجاح', 'success')
            return redirect(url_for('categories'))
            
        except Exception as e:
            flash(f'خطأ في إضافة الفئة: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('add_category.html')

@app.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    """تعديل فئة"""
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'POST':
        try:
            category.name = request.form['name']
            category.description = request.form.get('description', '')
            
            db.session.commit()
            flash('تم تحديث الفئة بنجاح', 'success')
            return redirect(url_for('categories'))
            
        except Exception as e:
            flash(f'خطأ في تحديث الفئة: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('edit_category.html', category=category)

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
def add_customer():
    """إضافة عميل جديد"""
    if request.method == 'POST':
        try:
            customer = Customer(
                name=request.form['name'],
                phone=request.form.get('phone', ''),
                email=request.form.get('email', ''),
                address=request.form.get('address', '')
            )
            
            db.session.add(customer)
            db.session.commit()
            flash('تم إضافة العميل بنجاح', 'success')
            return redirect(url_for('customers'))
            
        except Exception as e:
            flash(f'خطأ في إضافة العميل: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('add_customer.html')

@app.route('/customers/edit/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    """تعديل عميل"""
    customer = Customer.query.get_or_404(customer_id)
    
    if request.method == 'POST':
        try:
            customer.name = request.form['name']
            customer.phone = request.form.get('phone', '')
            customer.email = request.form.get('email', '')
            customer.address = request.form.get('address', '')
            
            db.session.commit()
            flash('تم تحديث العميل بنجاح', 'success')
            return redirect(url_for('customers'))
            
        except Exception as e:
            flash(f'خطأ في تحديث العميل: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('edit_customer.html', customer=customer)

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
def add_supplier():
    """إضافة مورد جديد"""
    if request.method == 'POST':
        try:
            supplier = Supplier(
                name=request.form['name'],
                company=request.form.get('company', ''),
                phone=request.form.get('phone', ''),
                email=request.form.get('email', ''),
                address=request.form.get('address', '')
            )
            
            db.session.add(supplier)
            db.session.commit()
            flash('تم إضافة المورد بنجاح', 'success')
            return redirect(url_for('suppliers'))
            
        except Exception as e:
            flash(f'خطأ في إضافة المورد: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('add_supplier.html')

@app.route('/suppliers/edit/<int:supplier_id>', methods=['GET', 'POST'])
def edit_supplier(supplier_id):
    """تعديل مورد"""
    supplier = Supplier.query.get_or_404(supplier_id)
    
    if request.method == 'POST':
        try:
            supplier.name = request.form['name']
            supplier.company = request.form.get('company', '')
            supplier.phone = request.form.get('phone', '')
            supplier.email = request.form.get('email', '')
            supplier.address = request.form.get('address', '')
            
            db.session.commit()
            flash('تم تحديث المورد بنجاح', 'success')
            return redirect(url_for('suppliers'))
            
        except Exception as e:
            flash(f'خطأ في تحديث المورد: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('edit_supplier.html', supplier=supplier)

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
def new_sale():
    """إنشاء فاتورة بيع جديدة"""
    if request.method == 'POST':
        try:
            # إنشاء الفاتورة
            sale = Sale(
                customer_id=int(request.form['customer_id']) if request.form['customer_id'] else None,
                total_amount=float(request.form['total_amount']),
                discount=float(request.form.get('discount', 0)),
                final_amount=float(request.form['final_amount']),
                payment_method=request.form.get('payment_method', 'نقدي'),
                notes=request.form.get('notes', '')
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
    return render_template('new_sale.html', customers=customers, products=products)

@app.route('/sales/<int:sale_id>')
def view_sale(sale_id):
    """عرض تفاصيل الفاتورة"""
    sale = Sale.query.get_or_404(sale_id)
    return render_template('view_sale.html', sale=sale)

# ==================== التقارير ====================

@app.route('/reports')
def reports():
    """صفحة التقارير"""
    # تقرير المبيعات الشهرية
    current_month = datetime.now().replace(day=1)
    monthly_sales = Sale.query.filter(Sale.created_at >= current_month).all()
    monthly_revenue = sum(sale.final_amount for sale in monthly_sales)
    
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
                         low_stock=low_stock)

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
    app.run(debug=True, host='127.0.0.1', port=5000)