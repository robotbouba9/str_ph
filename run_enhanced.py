#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف تشغيل محسن لبرنامج إدارة مخزون محل الهواتف
Enhanced Run Script for Phone Store Inventory Management System
"""

import os
import sys
from app import app, db
from database import Category, Product, Supplier, Customer

def setup_database():
    """إعداد قاعدة البيانات مع البيانات المحسنة"""
    with app.app_context():
        # إنشاء الجداول
        db.create_all()
        
        # التحقق من وجود البيانات
        if Category.query.first() is None:
            print("🔄 إضافة البيانات التجريبية المحسنة...")
            
            # إضافة الفئات المحسنة
            categories = [
                Category(name='هواتف ذكية', description='الهواتف المحمولة الذكية بجميع أنواعها وماركاتها المختلفة'),
                Category(name='سماعات', description='سماعات الرأس والأذن السلكية واللاسلكية بجميع الأنواع'),
                Category(name='كابلات الشحن', description='كابلات الشحن والبيانات USB-C, Lightning, Micro USB'),
                Category(name='شواحن', description='شواحن الهواتف والأجهزة الإلكترونية السريعة والعادية'),
                Category(name='حافظات وجرابات', description='حافظات وجرابات الهواتف الواقية والأنيقة'),
                Category(name='اكسسوارات', description='اكسسوارات الهواتف المتنوعة مثل حوامل السيارة وحلقات الإصبع'),
                Category(name='بطاريات خارجية', description='بطاريات الشحن المحمولة (Power Banks) بسعات مختلفة'),
                Category(name='شاشات حماية', description='شاشات الحماية الزجاجية والبلاستيكية للهواتف')
            ]
            
            for category in categories:
                db.session.add(category)
            db.session.commit()
            
            # إضافة موردين محسنين
            suppliers = [
                Supplier(
                    name='أحمد محمد التكنولوجيا',
                    company='شركة الهواتف المتقدمة',
                    phone='01234567890',
                    email='ahmed@advanced-phones.com',
                    address='شارع التحرير، القاهرة، مصر'
                ),
                Supplier(
                    name='محمد علي الإلكترونيات',
                    company='مؤسسة التكنولوجيا الحديثة',
                    phone='01987654321',
                    email='mohamed@modern-tech.com',
                    address='كورنيش النيل، الإسكندرية، مصر'
                ),
                Supplier(
                    name='سارة أحمد للاكسسوارات',
                    company='شركة الاكسسوارات الذكية',
                    phone='01555666777',
                    email='sara@smart-accessories.com',
                    address='مدينة نصر، القاهرة، مصر'
                )
            ]
            
            for supplier in suppliers:
                db.session.add(supplier)
            db.session.commit()
            
            # إضافة عملاء محسنين
            customers = [
                Customer(
                    name='سارة أحمد محمد',
                    phone='01111111111',
                    email='sara.ahmed@email.com',
                    address='المعادي، القاهرة'
                ),
                Customer(
                    name='محمد حسن علي',
                    phone='01222222222',
                    email='mohamed.hassan@email.com',
                    address='المهندسين، الجيزة'
                ),
                Customer(
                    name='فاطمة عبدالله',
                    phone='01333333333',
                    email='fatma.abdullah@email.com',
                    address='مصر الجديدة، القاهرة'
                ),
                Customer(
                    name='أحمد محمود',
                    phone='01444444444',
                    email='ahmed.mahmoud@email.com',
                    address='الدقي، الجيزة'
                )
            ]
            
            for customer in customers:
                db.session.add(customer)
            db.session.commit()
            
            # الحصول على الفئات والموردين
            phone_category = Category.query.filter_by(name='هواتف ذكية').first()
            headphones_category = Category.query.filter_by(name='سماعات').first()
            cable_category = Category.query.filter_by(name='كابلات الشحن').first()
            charger_category = Category.query.filter_by(name='شواحن').first()
            case_category = Category.query.filter_by(name='حافظات وجرابات').first()
            powerbank_category = Category.query.filter_by(name='بطاريات خارجية').first()
            
            supplier1 = suppliers[0]
            supplier2 = suppliers[1]
            supplier3 = suppliers[2]
            
            # إضافة منتجات محسنة ومتنوعة
            products = [
                # هواتف ذكية
                Product(
                    name='iPhone 15 Pro Max',
                    brand='Apple',
                    model='iPhone 15 Pro Max',
                    color='أزرق تيتانيوم',
                    description='شاشة 6.7 بوصة Super Retina XDR، معالج A17 Pro، كاميرا ثلاثية 48MP، ذاكرة 256GB، مقاوم للماء IP68، دعم 5G',
                    price_buy=48000,
                    price_sell=55000,
                    quantity=8,
                    min_quantity=3,
                    barcode='1001001001',
                    category_id=phone_category.id,
                    supplier_id=supplier1.id
                ),
                Product(
                    name='Samsung Galaxy S24 Ultra',
                    brand='Samsung',
                    model='Galaxy S24 Ultra',
                    color='أسود تيتانيوم',
                    description='شاشة 6.8 بوصة Dynamic AMOLED، معالج Snapdragon 8 Gen 3، كاميرا رباعية 200MP، ذاكرة 512GB، قلم S Pen، مقاوم للماء IP68',
                    price_buy=42000,
                    price_sell=48000,
                    quantity=12,
                    min_quantity=4,
                    barcode='1001001002',
                    category_id=phone_category.id,
                    supplier_id=supplier2.id
                ),
                Product(
                    name='Xiaomi 14 Pro',
                    brand='Xiaomi',
                    model='14 Pro',
                    color='أبيض سيراميك',
                    description='شاشة 6.73 بوصة AMOLED، معالج Snapdragon 8 Gen 3، كاميرا ثلاثية 50MP، ذاكرة 256GB، شحن سريع 120W',
                    price_buy=22000,
                    price_sell=26000,
                    quantity=15,
                    min_quantity=5,
                    barcode='1001001003',
                    category_id=phone_category.id,
                    supplier_id=supplier1.id
                ),
                
                # سماعات
                Product(
                    name='AirPods Pro 2nd Gen',
                    brand='Apple',
                    model='AirPods Pro 2',
                    color='أبيض',
                    description='سماعات لاسلكية مع إلغاء الضوضاء النشط، شريحة H2، مقاومة للعرق والماء IPX4، علبة شحن MagSafe، عمر البطارية 6 ساعات',
                    price_buy=8500,
                    price_sell=11000,
                    quantity=20,
                    min_quantity=6,
                    barcode='2001001001',
                    category_id=headphones_category.id,
                    supplier_id=supplier1.id
                ),
                Product(
                    name='Sony WH-1000XM5',
                    brand='Sony',
                    model='WH-1000XM5',
                    color='أسود',
                    description='سماعات رأس لاسلكية مع إلغاء الضوضاء الرائد في الصناعة، عمر البطارية 30 ساعة، شحن سريع، مكالمات عالية الوضوح',
                    price_buy=12000,
                    price_sell=15500,
                    quantity=8,
                    min_quantity=3,
                    barcode='2001001002',
                    category_id=headphones_category.id,
                    supplier_id=supplier2.id
                ),
                
                # كابلات الشحن
                Product(
                    name='كابل USB-C إلى Lightning أصلي',
                    brand='Apple',
                    model='USB-C to Lightning Cable',
                    color='أبيض',
                    description='كابل شحن ونقل بيانات أصلي من Apple، طول 2 متر، يدعم الشحن السريع حتى 20W، متوافق مع جميع أجهزة iPhone وiPad',
                    price_buy=180,
                    price_sell=280,
                    quantity=50,
                    min_quantity=15,
                    barcode='3001001001',
                    category_id=cable_category.id,
                    supplier_id=supplier3.id
                ),
                Product(
                    name='كابل USB-C إلى USB-C سريع',
                    brand='Samsung',
                    model='USB-C Fast Cable',
                    color='أسود',
                    description='كابل شحن سريع USB-C إلى USB-C، طول 1.5 متر، يدعم الشحن السريع حتى 45W، نقل البيانات عالي السرعة',
                    price_buy=120,
                    price_sell=200,
                    quantity=75,
                    min_quantity=20,
                    barcode='3001001002',
                    category_id=cable_category.id,
                    supplier_id=supplier2.id
                ),
                
                # شواحن
                Product(
                    name='شاحن سريع 65W USB-C',
                    brand='Anker',
                    model='PowerPort III 65W',
                    color='أبيض',
                    description='شاحن سريع بقوة 65W، منفذ USB-C واحد، يدعم تقنية Power Delivery، متوافق مع الهواتف واللابتوب، حماية متعددة المستويات',
                    price_buy=350,
                    price_sell=500,
                    quantity=25,
                    min_quantity=8,
                    barcode='4001001001',
                    category_id=charger_category.id,
                    supplier_id=supplier3.id
                ),
                
                # حافظات
                Product(
                    name='حافظة iPhone 15 Pro جلدية',
                    brand='Apple',
                    model='Leather Case iPhone 15 Pro',
                    color='أزرق منتصف الليل',
                    description='حافظة جلدية أصلية من Apple، حماية ممتازة، تصميم أنيق، متوافقة مع MagSafe، جلد طبيعي عالي الجودة',
                    price_buy=280,
                    price_sell=420,
                    quantity=30,
                    min_quantity=10,
                    barcode='5001001001',
                    category_id=case_category.id,
                    supplier_id=supplier3.id
                ),
                
                # بطاريات خارجية
                Product(
                    name='بطارية خارجية 20000mAh',
                    brand='Anker',
                    model='PowerCore 20000',
                    color='أسود',
                    description='بطارية شحن محمولة بسعة 20000mAh، منفذين USB-A ومنفذ USB-C، شحن سريع، شاشة LED لعرض مستوى البطارية',
                    price_buy=450,
                    price_sell=650,
                    quantity=18,
                    min_quantity=6,
                    barcode='6001001001',
                    category_id=powerbank_category.id,
                    supplier_id=supplier3.id
                )
            ]
            
            for product in products:
                db.session.add(product)
            
            db.session.commit()
            print("✅ تم إضافة البيانات التجريبية المحسنة بنجاح!")
            print(f"📊 تم إضافة:")
            print(f"   • {len(categories)} فئات")
            print(f"   • {len(suppliers)} موردين") 
            print(f"   • {len(customers)} عملاء")
            print(f"   • {len(products)} منتجات")
        else:
            print("✅ قاعدة البيانات جاهزة!")

def main():
    """الدالة الرئيسية لتشغيل البرنامج"""
    print("بدء تشغيل برنامج إدارة مخزون محل الهواتف المحسن")
    print("=" * 60)
    
    # إعداد قاعدة البيانات
    setup_database()
    
    print("\nالبرنامج متاح على:")
    print("   • http://127.0.0.1:5000")
    print("   • http://localhost:5000")
    print("\nالمميزات الجديدة:")
    print("   • نظام الفئات المحسن")
    print("   • البحث التلقائي السريع")
    print("   • وصف مفصل للمنتجات")
    print("   • الأرقام بالتنسيق الإنجليزي")
    print("   • تصميم محسن ومتناسق")
    print("\nلإيقاف: اضغط Ctrl+C")
    print("=" * 60)
    
    # تشغيل التطبيق
    try:
        app.run(debug=True, host='127.0.0.1', port=5000)
    except KeyboardInterrupt:
        print("\n\nتم إيقاف البرنامج بنجاح!")
        print("شكراً لاستخدام برنامج إدارة مخزون محل الهواتف!")

if __name__ == '__main__':
    main()