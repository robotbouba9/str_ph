#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إنشاء بيانات تجريبية للاختبار
"""

import sys
import os
from datetime import datetime, timedelta

def create_test_data():
    """إنشاء بيانات تجريبية"""
    print("📊 إنشاء بيانات تجريبية للاختبار")
    print("=" * 40)
    
    try:
        from app import app
        from database import db, Product, Customer, Supplier, Sale, SaleItem, Category, PurchaseInvoice, PurchaseItem
        
        with app.app_context():
            # إنشاء الجداول إذا لم تكن موجودة
            db.create_all()
            
            # فحص وجود بيانات
            existing_products = Product.query.count()
            existing_sales = Sale.query.count()
            
            print(f"📦 المنتجات الموجودة: {existing_products}")
            print(f"🧾 المبيعات الموجودة: {existing_sales}")
            
            if existing_products == 0:
                print("📦 إنشاء منتجات تجريبية...")
                
                # إنشاء فئة
                category = Category(name="هواتف ذكية", description="هواتف محمولة")
                db.session.add(category)
                db.session.commit()
                
                # إنشاء منتجات
                products = [
                    Product(name="iPhone 15 Pro Max 256GB", category_id=category.id, 
                           purchase_price=150000, selling_price=180000, quantity=10, min_quantity=2),
                    Product(name="Samsung Galaxy S24 Ultra", category_id=category.id,
                           purchase_price=120000, selling_price=150000, quantity=8, min_quantity=2),
                    Product(name="Wireless Charger", category_id=category.id,
                           purchase_price=3000, selling_price=5000, quantity=20, min_quantity=5)
                ]
                
                for product in products:
                    db.session.add(product)
                
                db.session.commit()
                print("✅ تم إنشاء المنتجات")
            
            if existing_sales == 0:
                print("🧾 إنشاء مبيعات تجريبية...")
                
                # إنشاء عميل
                customer = Customer(name="أحمد محمد", phone="+213555123456", 
                                  email="ahmed@example.com", address="الجزائر العاصمة")
                db.session.add(customer)
                db.session.commit()
                
                # إنشاء مورد
                supplier = Supplier(name="مورد الهواتف", phone="+213555987654",
                                  email="supplier@example.com", address="وهران")
                db.session.add(supplier)
                db.session.commit()
                
                # الحصول على المنتجات
                products = Product.query.all()
                
                if products:
                    # إنشاء مبيعة
                    sale = Sale(customer_id=customer.id, payment_method="نقداً", 
                               notes="فاتورة تجريبية للاختبار")
                    db.session.add(sale)
                    db.session.commit()
                    
                    # إضافة عناصر المبيعة
                    sale_items = [
                        SaleItem(sale_id=sale.id, product_id=products[0].id, 
                                quantity=1, unit_price=products[0].selling_price),
                        SaleItem(sale_id=sale.id, product_id=products[2].id,
                                quantity=2, unit_price=products[2].selling_price)
                    ]
                    
                    for item in sale_items:
                        db.session.add(item)
                    
                    # حساب المجاميع
                    sale.total_amount = sum(item.quantity * item.unit_price for item in sale_items)
                    sale.discount = 5000
                    sale.final_amount = sale.total_amount - sale.discount
                    
                    db.session.commit()
                    print("✅ تم إنشاء مبيعة تجريبية")
                    
                    # إنشاء فاتورة شراء
                    purchase = PurchaseInvoice(supplier_id=supplier.id, invoice_number="PUR-000001",
                                             payment_method="نقداً", notes="فاتورة شراء تجريبية")
                    db.session.add(purchase)
                    db.session.commit()
                    
                    # إضافة عناصر الشراء
                    purchase_item = PurchaseItem(purchase_id=purchase.id, product_id=products[0].id,
                                               quantity=5, unit_price=products[0].purchase_price)
                    db.session.add(purchase_item)
                    
                    # حساب المجاميع
                    purchase.total_amount = purchase_item.quantity * purchase_item.unit_price
                    purchase.discount = 0
                    purchase.final_amount = purchase.total_amount
                    
                    db.session.commit()
                    print("✅ تم إنشاء فاتورة شراء تجريبية")
            
            # عرض الإحصائيات النهائية
            final_products = Product.query.count()
            final_sales = Sale.query.count()
            final_purchases = PurchaseInvoice.query.count()
            
            print()
            print("📊 الإحصائيات النهائية:")
            print(f"   📦 المنتجات: {final_products}")
            print(f"   🧾 المبيعات: {final_sales}")
            print(f"   📋 المشتريات: {final_purchases}")
            
            # إزالة اختبارات الطباعة الحرارية بعد الاستغناء عنها
            
            print()
            print("🎉 تم إنشاء البيانات التجريبية بنجاح!")
            print("🌐 يمكنك الآن اختبار التطبيق على: http://127.0.0.1:5000")
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في إنشاء البيانات: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    create_test_data()