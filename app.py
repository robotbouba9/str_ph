# -*- coding: utf-8 -*-
"""
تطبيق Flask لإدارة مخزون محل الهواتف
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from database import db, init_database, Product, Customer, Supplier, Sale, SaleItem, Category
from datetime import datetime, timedelta
import os

# إعداد التطبيق
app = Flask(__name__)

# محاولة استيراد الإعدادات، وإذا فشلت استخدم الإعدادات الافتراضية
try:
    from config import config, MESSAGES
    app.config.from_object(config['development'])
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

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)