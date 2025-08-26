# -*- coding: utf-8 -*-
"""
قاعدة البيانات لبرنامج إدارة مخزون محل الهواتف
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
import os

db = SQLAlchemy()

class User(db.Model):
    """مستخدمو النظام وأدوارهم"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='worker')  # owner, worker, technician
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

class StoreSettings(db.Model):
    """إعدادات المتجر العامة"""
    __tablename__ = 'store_settings'

    id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(200), default='MOBILE PHONE STORE')
    store_name_ar = db.Column(db.String(200), default='متجر الهواتف')
    address = db.Column(db.String(300), default='Algiers, Algeria')
    phone = db.Column(db.String(50), default='+213 123 456 789')
    email = db.Column(db.String(120))
    currency_name = db.Column(db.String(50), default='دينار جزائري')
    currency_symbol = db.Column(db.String(10), default='د.ج')
    logo_path = db.Column(db.String(300))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'store_name': self.store_name,
            'store_name_ar': self.store_name_ar,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'currency_name': self.currency_name,
            'currency_symbol': self.currency_symbol,
            'logo_path': self.logo_path,
        }

class Category(db.Model):
    """جدول الفئات"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # اسم الفئة
    description = db.Column(db.Text)  # وصف الفئة
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    products = db.relationship('Product', backref='category')
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'products_count': len(self.products)
        }

class Brand(db.Model):
    """جدول الماركات"""
    __tablename__ = 'brands'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Brand {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }

class Product(db.Model):
    """جدول المنتجات"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # اسم المنتج
    brand = db.Column(db.String(100), nullable=False)  # الماركة
    model = db.Column(db.String(100), nullable=False)  # الموديل
    color = db.Column(db.String(50))  # اللون
    description = db.Column(db.Text)  # وصف المنتج ومواصفاته
    price_buy = db.Column(db.Float, nullable=False)  # سعر الشراء
    price_sell = db.Column(db.Float, nullable=False)  # سعر البيع
    quantity = db.Column(db.Integer, default=0)  # الكمية المتوفرة
    min_quantity = db.Column(db.Integer, default=5)  # الحد الأدنى للكمية
    barcode = db.Column(db.String(100), unique=True)  # الباركود
    imei = db.Column(db.String(100), unique=True, nullable=True) # رقم IMEI
    warranty_period = db.Column(db.Integer, default=0) # مدة الضمان بالأيام
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))  # الفئة
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    supplier = db.relationship('Supplier', backref='products')
    sale_items = db.relationship('SaleItem', backref='product')
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'model': self.model,
            'color': self.color,
            'description': self.description,
            'price_buy': self.price_buy,
            'price_sell': self.price_sell,
            'quantity': self.quantity,
            'min_quantity': self.min_quantity,
            'barcode': self.barcode,
            'imei': self.imei,
            'warranty_period': self.warranty_period,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else '',
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else ''
        }

class Customer(db.Model):
    """جدول العملاء"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # اسم العميل
    phone = db.Column(db.String(20))  # رقم الهاتف
    email = db.Column(db.String(100))  # البريد الإلكتروني
    address = db.Column(db.Text)  # العنوان
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    sales = db.relationship('Sale', backref='customer')
    
    def __repr__(self):
        return f'<Customer {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }

class Supplier(db.Model):
    """جدول الموردين"""
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # اسم المورد
    company = db.Column(db.String(200))  # اسم الشركة
    phone = db.Column(db.String(20))  # رقم الهاتف
    email = db.Column(db.String(100))  # البريد الإلكتروني
    address = db.Column(db.Text)  # العنوان
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Supplier {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'company': self.company,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }

class Sale(db.Model):
    """جدول المبيعات"""
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    total_amount = db.Column(db.Float, nullable=False)  # المبلغ الإجمالي
    discount = db.Column(db.Float, default=0)  # الخصم
    final_amount = db.Column(db.Float, nullable=False)  # المبلغ النهائي
    payment_method = db.Column(db.String(50), default='نقدي')  # طريقة الدفع
    notes = db.Column(db.Text)  # ملاحظات
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    sale_items = db.relationship('SaleItem', backref='sale', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Sale {self.id}>'

class Return(db.Model):
    """جدول المرتجعات"""
    __tablename__ = 'returns'

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False) # المبيعة الأصلية
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id')) # العميل الذي قام بالارجاع
    return_date = db.Column(db.DateTime, default=datetime.utcnow) # تاريخ الارجاع
    total_amount = db.Column(db.Float, nullable=False) # المبلغ الإجمالي للمرتجع
    reason = db.Column(db.Text) # سبب الارجاع
    notes = db.Column(db.Text) # ملاحظات إضافية

    # العلاقات
    sale = db.relationship('Sale', backref='returns')
    customer = db.relationship('Customer', backref='returns')
    return_items = db.relationship('ReturnItem', backref='return', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Return {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'sale_id': self.sale_id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else 'N/A',
            'return_date': self.return_date.strftime('%Y-%m-%d %H:%M:%S') if self.return_date else '',
            'total_amount': self.total_amount,
            'reason': self.reason,
            'notes': self.notes
        }

class ReturnItem(db.Model):
    """تفاصيل المنتجات المرتجعة"""
    __tablename__ = 'return_items'

    id = db.Column(db.Integer, primary_key=True)
    return_id = db.Column(db.Integer, db.ForeignKey('returns.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False) # الكمية المرتجعة
    price = db.Column(db.Float, nullable=False) # سعر الوحدة وقت الارجاع

    # العلاقات
    product = db.relationship('Product', backref='return_items')

    def __repr__(self):
        return f'<ReturnItem {self.id} - Product {self.product_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'return_id': self.return_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'N/A',
            'quantity': self.quantity,
            'price': self.price
        }
    


class SaleItem(db.Model):
    """جدول عناصر المبيعات"""
    __tablename__ = 'sale_items'
    
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)  # الكمية المباعة
    unit_price = db.Column(db.Float, nullable=False)  # سعر الوحدة
    total_price = db.Column(db.Float, nullable=False)  # السعر الإجمالي
    
    def __repr__(self):
        return f'<SaleItem {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'sale_id': self.sale_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else '',
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price
        }

class PurchaseInvoice(db.Model):
    """جدول فواتير الشراء من الموردين"""
    __tablename__ = 'purchase_invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    invoice_number = db.Column(db.String(100), unique=True)  # رقم الفاتورة
    total_amount = db.Column(db.Float, nullable=False)  # المبلغ الإجمالي
    discount = db.Column(db.Float, default=0)  # الخصم
    final_amount = db.Column(db.Float, nullable=False)  # المبلغ النهائي
    payment_method = db.Column(db.String(50), default='نقدي')  # طريقة الدفع
    notes = db.Column(db.Text)  # ملاحظات
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    supplier = db.relationship('Supplier', backref='purchase_invoices')
    purchase_items = db.relationship('PurchaseItem', backref='purchase_invoice', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<PurchaseInvoice {self.invoice_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else '',
            'invoice_number': self.invoice_number,
            'total_amount': self.total_amount,
            'discount': self.discount,
            'final_amount': self.final_amount,
            'payment_method': self.payment_method,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'items': [item.to_dict() for item in self.purchase_items]
        }

class PurchaseItem(db.Model):
    """جدول عناصر فواتير الشراء"""
    __tablename__ = 'purchase_items'
    
    id = db.Column(db.Integer, primary_key=True)
    purchase_invoice_id = db.Column(db.Integer, db.ForeignKey('purchase_invoices.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)  # الكمية المشتراة
    unit_price = db.Column(db.Float, nullable=False)  # سعر الوحدة
    total_price = db.Column(db.Float, nullable=False)  # السعر الإجمالي
    
    # العلاقات
    product = db.relationship('Product', backref='purchase_items')
    
    def __repr__(self):
        return f'<PurchaseItem {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'purchase_invoice_id': self.purchase_invoice_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else '',
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price
        }

def init_database(app):
    """تهيئة قاعدة البيانات"""
    db.init_app(app)
    
    # لا ننشئ الجداول تلقائياً، سيتم إنشاؤها عند الحاجة
    return db

def create_tables(app):
    """إنشاء الجداول وإضافة البيانات الافتراضية"""
    with app.app_context():
        # إنشاء الجداول
        db.create_all()
        
        # إنشاء سجل إعدادات افتراضي إن لم يوجد
        if not StoreSettings.query.first():
            settings = StoreSettings()
            db.session.add(settings)
            db.session.commit()

        # إنشاء مستخدم admin افتراضي
        from werkzeug.security import generate_password_hash
        if not User.query.filter_by(username='admin').first():
            user = User(username='admin', password_hash=generate_password_hash('Admin@123'), role='admin', is_active=True)
            db.session.add(user)
            db.session.commit()

        # إضافة بيانات تجريبية إذا كانت قاعدة البيانات فارغة
        if not Supplier.query.first():
            add_sample_data()

class Notification(db.Model):
    """جدول الإشعارات"""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # low_stock, sale, return, etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # العلاقات
    user = db.relationship('User', backref='notifications')
    product = db.relationship('Product', backref='notifications')

    def __repr__(self):
        return f'<Notification {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'read': self.read,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else ''
        }

class ActivityLog(db.Model):
    """جدول سجل الأنشطة"""
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)  # create, update, delete
    entity_type = db.Column(db.String(50), nullable=False)  # product, customer, sale, etc.
    entity_id = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # العلاقات
    user = db.relationship('User', backref='activity_logs')

    def __repr__(self):
        return f'<ActivityLog {self.action} {self.entity_type}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Unknown',
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'description': self.description,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else ''
        }

class AuditLog(db.Model):
    """جدول سجل المراجعة"""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(20), nullable=False)  # INSERT, UPDATE, DELETE
    old_values = db.Column(db.Text)  # JSON string of old values
    new_values = db.Column(db.Text)  # JSON string of new values
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # العلاقات
    user = db.relationship('User', backref='audit_logs')

    def __repr__(self):
        return f'<AuditLog {self.action} {self.table_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Unknown',
            'table_name': self.table_name,
            'record_id': self.record_id,
            'action': self.action,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else ''
        }

def add_sample_data():
    """إضافة بيانات تجريبية"""
    try:
        # إضافة الفئات
        categories = [
            Category(name='هواتف ذكية', description='الهواتف المحمولة الذكية بجميع أنواعها'),
            Category(name='سماعات', description='سماعات الرأس والأذن السلكية واللاسلكية'),
            Category(name='كابلات الشحن', description='كابلات الشحن والبيانات بجميع الأنواع'),
            Category(name='شواحن', description='شواحن الهواتف والأجهزة الإلكترونية'),
            Category(name='حافظات وجرابات', description='حافظات وجرابات الهواتف الواقية'),
            Category(name='اكسسوارات', description='اكسسوارات الهواتف المتنوعة')
        ]
        
        for category in categories:
            db.session.add(category)
        db.session.commit()
        
        # إضافة موردين
        supplier1 = Supplier(
            name='أحمد محمد',
            company='شركة الهواتف المتقدمة',
            phone='01234567890',
            email='ahmed@phones.com',
            address='القاهرة، مصر'
        )
        
        supplier2 = Supplier(
            name='محمد علي',
            company='مؤسسة التكنولوجيا الحديثة',
            phone='01987654321',
            email='mohamed@tech.com',
            address='الإسكندرية، مصر'
        )
        
        db.session.add(supplier1)
        db.session.add(supplier2)
        db.session.commit()
        
        # إضافة عملاء
        customer1 = Customer(
            name='سارة أحمد',
            phone='01111111111',
            email='sara@email.com',
            address='المعادي، القاهرة'
        )
        
        customer2 = Customer(
            name='محمد حسن',
            phone='01222222222',
            email='mohamed@email.com',
            address='المهندسين، الجيزة'
        )
        
        db.session.add(customer1)
        db.session.add(customer2)
        db.session.commit()
        
        # الحصول على الفئات المضافة
        phone_category = Category.query.filter_by(name='هواتف ذكية').first()
        headphones_category = Category.query.filter_by(name='سماعات').first()
        cable_category = Category.query.filter_by(name='كابلات الشحن').first()
        charger_category = Category.query.filter_by(name='شواحن').first()
        
        # إضافة منتجات
        products = [
            Product(
                name='iPhone 15 Pro',
                brand='Apple',
                model='iPhone 15 Pro',
                color='أزرق تيتانيوم',
                description='شاشة 6.1 بوصة Super Retina XDR، معالج A17 Pro، كاميرا ثلاثية 48MP، ذاكرة 256GB، مقاوم للماء IP68',
                price_buy=45000,
                price_sell=52000,
                quantity=10,
                min_quantity=3,
                barcode='1234567890123',
                category_id=phone_category.id if phone_category else None,
                supplier_id=supplier1.id
            ),
            Product(
                name='Samsung Galaxy S24',
                brand='Samsung',
                model='Galaxy S24',
                color='أسود',
                description='شاشة 6.2 بوصة Dynamic AMOLED، معالج Snapdragon 8 Gen 3، كاميرا ثلاثية 50MP، ذاكرة 128GB، مقاوم للماء IP68',
                price_buy=25000,
                price_sell=30000,
                quantity=15,
                min_quantity=5,
                barcode='1234567890124',
                category_id=phone_category.id if phone_category else None,
                supplier_id=supplier2.id
            ),
            Product(
                name='AirPods Pro 2',
                brand='Apple',
                model='AirPods Pro 2nd Gen',
                color='أبيض',
                description='سماعات لاسلكية مع إلغاء الضوضاء النشط، شريحة H2، مقاومة للعرق والماء IPX4، علبة شحن MagSafe',
                price_buy=8000,
                price_sell=10500,
                quantity=12,
                min_quantity=4,
                barcode='1234567890125',
                category_id=headphones_category.id if headphones_category else None,
                supplier_id=supplier1.id
            ),
            Product(
                name='كابل USB-C إلى Lightning',
                brand='Apple',
                model='USB-C to Lightning Cable',
                color='أبيض',
                description='كابل شحن ونقل بيانات أصلي من Apple، طول 1 متر، يدعم الشحن السريع حتى 20W، متوافق مع جميع أجهزة iPhone',
                price_buy=150,
                price_sell=250,
                quantity=50,
                min_quantity=10,
                barcode='1234567890126',
                category_id=cable_category.id if cable_category else None,
                supplier_id=supplier2.id
            ),
            Product(
                name='شاحن سريع 25W',
                brand='Samsung',
                model='EP-TA800',
                color='أسود',
                description='شاحن سريع أصلي من Samsung بقوة 25W، منفذ USB-C، يدعم تقنية Power Delivery، متوافق مع جميع الأجهزة',
                price_buy=200,
                price_sell=350,
                quantity=25,
                min_quantity=8,
                barcode='1234567890127',
                category_id=charger_category.id if charger_category else None,
                supplier_id=supplier1.id
            )
        ]
        
        for product in products:
            db.session.add(product)
        
        db.session.commit()
        print("تم إضافة البيانات التجريبية بنجاح")
        
    except Exception as e:
        print(f"خطأ في إضافة البيانات التجريبية: {e}")
        db.session.rollback()