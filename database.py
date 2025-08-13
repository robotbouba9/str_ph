# -*- coding: utf-8 -*-
"""
قاعدة البيانات لبرنامج إدارة مخزون محل الهواتف
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
import os

db = SQLAlchemy()

class Product(db.Model):
    """جدول المنتجات (الهواتف)"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # اسم الهاتف
    brand = db.Column(db.String(100), nullable=False)  # الماركة
    model = db.Column(db.String(100), nullable=False)  # الموديل
    color = db.Column(db.String(50))  # اللون
    storage = db.Column(db.String(50))  # مساحة التخزين
    price_buy = db.Column(db.Float, nullable=False)  # سعر الشراء
    price_sell = db.Column(db.Float, nullable=False)  # سعر البيع
    quantity = db.Column(db.Integer, default=0)  # الكمية المتوفرة
    min_quantity = db.Column(db.Integer, default=5)  # الحد الأدنى للكمية
    barcode = db.Column(db.String(100), unique=True)  # الباركود
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
            'storage': self.storage,
            'price_buy': self.price_buy,
            'price_sell': self.price_sell,
            'quantity': self.quantity,
            'min_quantity': self.min_quantity,
            'barcode': self.barcode,
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else 'عميل غير محدد',
            'total_amount': self.total_amount,
            'discount': self.discount,
            'final_amount': self.final_amount,
            'payment_method': self.payment_method,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'items': [item.to_dict() for item in self.sale_items]
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

def init_database(app):
    """تهيئة قاعدة البيانات"""
    db.init_app(app)
    
    with app.app_context():
        # إنشاء الجداول
        db.create_all()
        
        # إضافة بيانات تجريبية إذا كانت قاعدة البيانات فارغة
        if not Supplier.query.first():
            add_sample_data()

def add_sample_data():
    """إضافة بيانات تجريبية"""
    try:
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
        
        # إضافة منتجات
        products = [
            Product(
                name='iPhone 15 Pro',
                brand='Apple',
                model='iPhone 15 Pro',
                color='أزرق تيتانيوم',
                storage='256GB',
                price_buy=45000,
                price_sell=52000,
                quantity=10,
                min_quantity=3,
                barcode='1234567890123',
                supplier_id=supplier1.id
            ),
            Product(
                name='Samsung Galaxy S24',
                brand='Samsung',
                model='Galaxy S24',
                color='أسود',
                storage='128GB',
                price_buy=25000,
                price_sell=30000,
                quantity=15,
                min_quantity=5,
                barcode='1234567890124',
                supplier_id=supplier2.id
            ),
            Product(
                name='Xiaomi 14',
                brand='Xiaomi',
                model='14',
                color='أبيض',
                storage='256GB',
                price_buy=18000,
                price_sell=22000,
                quantity=8,
                min_quantity=3,
                barcode='1234567890125',
                supplier_id=supplier1.id
            ),
            Product(
                name='Huawei P60 Pro',
                brand='Huawei',
                model='P60 Pro',
                color='ذهبي',
                storage='512GB',
                price_buy=28000,
                price_sell=35000,
                quantity=5,
                min_quantity=2,
                barcode='1234567890126',
                supplier_id=supplier2.id
            )
        ]
        
        for product in products:
            db.session.add(product)
        
        db.session.commit()
        print("تم إضافة البيانات التجريبية بنجاح")
        
    except Exception as e:
        print(f"خطأ في إضافة البيانات التجريبية: {e}")
        db.session.rollback()