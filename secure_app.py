# -*- coding: utf-8 -*-
"""
خادم Flask آمن للإنتاج - برنامج إدارة مخزون محل الهواتف
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from database import db, init_database, Product, Customer, Supplier, Sale, SaleItem
from datetime import datetime, timedelta
import os
import secrets
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# إعداد التطبيق الآمن
app = Flask(__name__)

# إعدادات الأمان المتقدمة
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY') or secrets.token_hex(32),
    SQLALCHEMY_DATABASE_URI='sqlite:///phone_store.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    
    # إعدادات الأمان
    SESSION_COOKIE_SECURE=False,  # True في HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    
    # حماية من الهجمات
    WTF_CSRF_ENABLED=True,
    WTF_CSRF_TIME_LIMIT=None,
    
    # إعدادات الخادم
    PREFERRED_URL_SCHEME='http',
    SERVER_NAME=None,
    
    # إعدادات التطبيق
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB
    SEND_FILE_MAX_AGE_DEFAULT=31536000,  # 1 year
)

# تهيئة قاعدة البيانات
init_database(app)

# إعدادات الأمان الإضافية
@app.before_request
def security_headers():
    """إضافة headers الأمان"""
    pass

@app.after_request
def after_request(response):
    """إضافة headers الأمان بعد كل طلب"""
    # حماية من XSS
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # حماية HTTPS (يمكن تفعيلها عند استخدام HTTPS)
    # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # حماية المحتوى
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self';"
    )
    
    return response

# نظام المصادقة البسيط (للحماية الأساسية)
def require_auth(f):
    """decorator للمصادقة"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # في هذا الإصدار، نسمح بالوصول المباشر
        # يمكن إضافة نظام مصادقة متقدم لاحقاً
        return f(*args, **kwargs)
    return decorated_function

# الصفحة الرئيسية
@app.route('/')
@require_auth
def index():
    """الصفحة الرئيسية مع الإحصائيات"""
    try:
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
        
        return render_template('index.html',
                             total_products=total_products,
                             total_customers=total_customers,
                             total_suppliers=total_suppliers,
                             today_revenue=today_revenue,
                             today_sales_count=len(today_sales),
                             low_stock_products=low_stock_products,
                             recent_sales=recent_sales)
    except Exception as e:
        app.logger.error(f"خطأ في الصفحة الرئيسية: {e}")
        flash('حدث خطأ في تحميل البيانات', 'error')
        return render_template('index.html',
                             total_products=0,
                             total_customers=0,
                             total_suppliers=0,
                             today_revenue=0,
                             today_sales_count=0,
                             low_stock_products=[],
                             recent_sales=[])

# استيراد المسارات من التطبيق الأصلي
# نحتاج لاستيراد المسارات يدوياً لتجنب التعارض

# مسارات المنتجات
@app.route('/products')
@require_auth
def products():
    """صفحة المنتجات"""
    search = request.args.get('search', '')
    brand_filter = request.args.get('brand', '')
    page = request.args.get('page', 1, type=int)
    
    query = Product.query
    
    # فلتر البحث
    if search:
        query = query.filter(
            db.or_(
                Product.name.contains(search),
                Product.brand.contains(search),
                Product.model.contains(search),
                Product.barcode.contains(search)
            )
        )
    
    # فلتر الماركة
    if brand_filter:
        query = query.filter(Product.brand == brand_filter)
    
    # الحصول على جميع الماركات للفلتر
    brands = db.session.query(Product.brand).distinct().filter(Product.brand.isnot(None)).all()
    brands = [brand[0] for brand in brands if brand[0]]
    
    # الحصول على المنتجات
    products_paginated = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    # تمرير المنتجات كقائمة للقالب
    products_list = products_paginated.items
    
    return render_template('products.html', 
                         products=products_list, 
                         brands=brands,
                         search=search,
                         pagination=products_paginated)

@app.route('/add_product', methods=['GET', 'POST'])
@require_auth
def add_product():
    """إضافة منتج جديد"""
    if request.method == 'POST':
        try:
            product = Product(
                name=request.form['name'],
                brand=request.form['brand'],
                model=request.form['model'],
                price_sell=float(request.form['price_sell']),
                price_buy=float(request.form.get('price_buy', 0)),
                quantity=int(request.form['quantity']),
                min_quantity=int(request.form.get('min_quantity', 5)),
                barcode=request.form.get('barcode', ''),
                description=request.form.get('description', ''),
                color=request.form.get('color', ''),
                storage=request.form.get('storage', ''),
                supplier_id=request.form.get('supplier_id') or None
            )
            
            db.session.add(product)
            db.session.commit()
            
            flash('تم إضافة المنتج بنجاح', 'success')
            return redirect(url_for('products'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'خطأ في إضافة المنتج: {str(e)}', 'error')
    
    suppliers = Supplier.query.all()
    return render_template('add_product.html', suppliers=suppliers)

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@require_auth
def edit_product(product_id):
    """تعديل منتج"""
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        try:
            product.name = request.form['name']
            product.brand = request.form['brand']
            product.model = request.form['model']
            product.price_sell = float(request.form['price_sell'])
            product.price_buy = float(request.form.get('price_buy', 0))
            product.quantity = int(request.form['quantity'])
            product.min_quantity = int(request.form.get('min_quantity', 5))
            product.barcode = request.form.get('barcode', '')
            product.description = request.form.get('description', '')
            product.color = request.form.get('color', '')
            product.storage = request.form.get('storage', '')
            product.supplier_id = request.form.get('supplier_id') or None
            
            db.session.commit()
            
            flash('تم تحديث المنتج بنجاح', 'success')
            return redirect(url_for('products'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'خطأ في تحديث المنتج: {str(e)}', 'error')
    
    suppliers = Supplier.query.all()
    return render_template('edit_product.html', product=product, suppliers=suppliers)

@app.route('/delete_product/<int:product_id>', methods=['POST'])
@require_auth
def delete_product(product_id):
    """حذف منتج"""
    try:
        product = Product.query.get_or_404(product_id)
        
        # التحقق من وجود مبيعات مرتبطة
        sales_count = SaleItem.query.filter_by(product_id=product_id).count()
        if sales_count > 0:
            flash(f'لا يمكن حذف المنتج لأنه مرتبط بـ {sales_count} عملية بيع', 'error')
            return redirect(url_for('products'))
        
        db.session.delete(product)
        db.session.commit()
        
        flash('تم حذف المنتج بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'خطأ في حذف المنتج: {str(e)}', 'error')
    
    return redirect(url_for('products'))

# مسارات العملاء
@app.route('/customers')
@require_auth
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
    
    return render_template('customers.html', customers=customers, search=search)

@app.route('/add_customer', methods=['GET', 'POST'])
@require_auth
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
            db.session.rollback()
            flash(f'خطأ في إضافة العميل: {str(e)}', 'error')
    
    return render_template('add_customer.html')

# مسارات الموردين
@app.route('/suppliers')
@require_auth
def suppliers():
    """صفحة الموردين"""
    search = request.args.get('search', '')
    
    query = Supplier.query
    
    if search:
        query = query.filter(
            db.or_(
                Supplier.name.contains(search),
                Supplier.company.contains(search),
                Supplier.phone.contains(search),
                Supplier.email.contains(search)
            )
        )
    
    suppliers = query.order_by(Supplier.created_at.desc()).all()
    
    return render_template('suppliers.html', suppliers=suppliers, search=search)

@app.route('/add_supplier', methods=['GET', 'POST'])
@require_auth
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
            db.session.rollback()
            flash(f'خطأ في إضافة المورد: {str(e)}', 'error')
    
    return render_template('add_supplier.html')

# مسارات المبيعات
@app.route('/sales')
@require_auth
def sales():
    """صفحة المبيعات"""
    page = request.args.get('page', 1, type=int)
    
    sales = Sale.query.order_by(Sale.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('sales.html', sales=sales)

@app.route('/new_sale', methods=['GET', 'POST'])
@require_auth
def new_sale():
    """إنشاء فاتورة جديدة"""
    if request.method == 'POST':
        try:
            # إنشاء الفاتورة
            sale = Sale(
                customer_id=request.form.get('customer_id') or None,
                total_amount=0,
                discount=float(request.form.get('discount', 0)),
                final_amount=0,
                payment_method=request.form.get('payment_method', 'نقدي'),
                notes=request.form.get('notes', '')
            )
            
            db.session.add(sale)
            db.session.flush()  # للحصول على ID
            
            # إضافة عناصر الفاتورة
            total = 0
            products_data = request.form.getlist('products')
            quantities_data = request.form.getlist('quantities')
            
            for i, product_id in enumerate(products_data):
                if product_id and i < len(quantities_data):
                    product = Product.query.get(product_id)
                    quantity = int(quantities_data[i])
                    
                    if product and quantity > 0:
                        if product.quantity >= quantity:
                            # إنشاء عنصر الفاتورة
                            sale_item = SaleItem(
                                sale_id=sale.id,
                                product_id=product.id,
                                quantity=quantity,
                                unit_price=product.price,
                                total_price=product.price * quantity
                            )
                            
                            # تحديث المخزون
                            product.quantity -= quantity
                            
                            db.session.add(sale_item)
                            total += sale_item.total_price
                        else:
                            raise Exception(f'الكمية المطلوبة من {product.name} غير متوفرة')
            
            # تحديث إجمالي الفاتورة
            sale.total_amount = total
            sale.final_amount = total - sale.discount
            
            db.session.commit()
            
            flash('تم إنشاء الفاتورة بنجاح', 'success')
            return redirect(url_for('view_sale', sale_id=sale.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'خطأ في إنشاء الفاتورة: {str(e)}', 'error')
    
    products = Product.query.filter(Product.quantity > 0).all()
    customers = Customer.query.all()
    
    return render_template('new_sale.html', products=products, customers=customers)

@app.route('/view_sale/<int:sale_id>')
@require_auth
def view_sale(sale_id):
    """عرض فاتورة"""
    sale = Sale.query.get_or_404(sale_id)
    return render_template('view_sale.html', sale=sale)

# مسار التقارير
@app.route('/reports')
@require_auth
def reports():
    """صفحة التقارير"""
    # إحصائيات الشهر الحالي
    current_month = datetime.now().replace(day=1)
    monthly_sales = Sale.query.filter(Sale.created_at >= current_month).all()
    monthly_revenue = sum(sale.final_amount for sale in monthly_sales)
    monthly_sales_count = len(monthly_sales)
    
    # المنتجات منخفضة المخزون
    low_stock = Product.query.filter(Product.quantity <= Product.min_quantity).all()
    
    # المنتجات الأكثر مبيعاً
    top_products_query = db.session.query(
        Product.name,
        db.func.sum(SaleItem.quantity).label('total_sold')
    ).join(SaleItem).group_by(Product.id).order_by(
        db.func.sum(SaleItem.quantity).desc()
    ).limit(10).all()
    
    top_products = [(name, int(total)) for name, total in top_products_query]
    
    return render_template('reports.html',
                         monthly_revenue=monthly_revenue,
                         monthly_sales_count=monthly_sales_count,
                         low_stock=low_stock,
                         top_products=top_products)

# إعداد معالج الأخطاء
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

# API للتطبيق الخارجي (Electron)
@app.route('/api/status')
def api_status():
    """حالة الخادم"""
    return jsonify({
        'status': 'running',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stats')
@require_auth
def api_stats():
    """إحصائيات سريعة للـ API"""
    try:
        stats = {
            'products': Product.query.count(),
            'customers': Customer.query.count(),
            'suppliers': Supplier.query.count(),
            'sales': Sale.query.count(),
            'low_stock': Product.query.filter(Product.quantity <= Product.min_quantity).count(),
            'today_revenue': sum(sale.final_amount for sale in Sale.query.filter(
                db.func.date(Sale.created_at) == datetime.now().date()
            ).all())
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_app():
    """إنشاء التطبيق مع الإعدادات الآمنة"""
    
    # إنشاء الجداول إذا لم تكن موجودة
    with app.app_context():
        try:
            db.create_all()
            
            # إضافة البيانات التجريبية إذا كانت قاعدة البيانات فارغة
            if Product.query.count() == 0:
                from database import add_sample_data
                add_sample_data()
                print("✅ تم إضافة البيانات التجريبية بنجاح")
                
        except Exception as e:
            print(f"❌ خطأ في إعداد قاعدة البيانات: {e}")
    
    return app

def run_secure_server(host='127.0.0.1', port=5000, debug=False):
    """تشغيل الخادم الآمن"""
    
    if debug:
        # وضع التطوير
        print("🔧 تشغيل في وضع التطوير")
        app.run(host=host, port=port, debug=True, threaded=True)
    else:
        # وضع الإنتاج مع Waitress
        try:
            from waitress import serve
            print(f"🚀 تشغيل الخادم الآمن على http://{host}:{port}")
            print("📊 لوحة التحكم: http://127.0.0.1:5000")
            print("🔒 الخادم يعمل في وضع الإنتاج الآمن")
            print("⏹️  لإيقاف الخادم: اضغط Ctrl+C")
            
            serve(app, host=host, port=port, threads=6)
            
        except ImportError:
            print("⚠️ Waitress غير مثبت، سيتم استخدام خادم Flask")
            print("💡 لتثبيت Waitress: pip install waitress")
            app.run(host=host, port=port, debug=False, threaded=True)
        except Exception as e:
            print(f"❌ خطأ في تشغيل الخادم: {e}")
            return False
    
    return True

if __name__ == '__main__':
    # إنشاء التطبيق
    app = create_app()
    
    # تشغيل الخادم الآمن
    import sys
    debug_mode = '--debug' in sys.argv
    run_secure_server(debug=debug_mode)