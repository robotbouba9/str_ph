#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل نهائي للمشروع
"""

import sys
import os
from datetime import datetime

def test_all_features():
    """اختبار شامل لجميع المميزات"""
    print("🎯" + "="*60 + "🎯")
    print("🏪          اختبار شامل نهائي للمشروع          🏪")
    print("🎯" + "="*60 + "🎯")
    print()
    
    all_tests_passed = True
    
    # ==================== اختبار 1: المكتبات المطلوبة ====================
    print("📦 اختبار 1: المكتبات المطلوبة")
    print("-" * 40)
    
    required_modules = [
        ('flask', 'Flask'),
        ('reportlab', 'ReportLab'),
        ('openpyxl', 'OpenPyXL'),
        ('sqlalchemy', 'SQLAlchemy')
    ]
    
    for module_name, display_name in required_modules:
        try:
            __import__(module_name)
            print(f"✅ {display_name}")
        except ImportError:
            print(f"❌ {display_name} - غير مثبت")
            all_tests_passed = False
    
    print()
    
    # ==================== اختبار 2: ملفات المشروع ====================
    print("📁 اختبار 2: ملفات المشروع الأساسية")
    print("-" * 40)
    
    required_files = [
        'app.py',
        'thermal_invoice.py',
        'models.py',
        'database.py',
        'excel_export.py',
        'run_web.py',
        'requirements.txt'
    ]
    
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} - مفقود")
            all_tests_passed = False
    
    print()
    
    # ==================== اختبار 3: قوالب HTML ====================
    print("🎨 اختبار 3: قوالب HTML")
    print("-" * 40)
    
    template_files = [
        'templates/base.html',
        'templates/index.html',
        'templates/sales.html',
        'templates/view_sale.html',
        'templates/purchases.html',
        'templates/view_purchase.html'
    ]
    
    for template in template_files:
        if os.path.exists(template):
            print(f"✅ {template}")
        else:
            print(f"❌ {template} - مفقود")
            all_tests_passed = False
    
    print()
    
    # ==================== اختبار 4: الفواتير الحرارية ====================
    print("🧾 اختبار 4: الفواتير الحرارية")
    print("-" * 40)
    
    try:
        from thermal_invoice import (ThermalInvoice, convert_to_english_numbers, 
                                   format_currency_thermal, format_date_thermal)
        
        # اختبار إنشاء كائن الفاتورة
        thermal = ThermalInvoice()
        print(f"✅ إنشاء كائن ThermalInvoice - العرض: {thermal.width/3.527:.0f}mm")
        
        # اختبار تحويل الأرقام
        test_arabic = "١٢٣٤٥"
        test_english = convert_to_english_numbers(test_arabic)
        if test_english == "12345":
            print(f"✅ تحويل الأرقام: {test_arabic} → {test_english}")
        else:
            print(f"❌ تحويل الأرقام فشل: {test_arabic} → {test_english}")
            all_tests_passed = False
        
        # اختبار تنسيق العملة
        test_amount = 1234.56
        formatted_currency = format_currency_thermal(test_amount)
        if "1,235 DA" in formatted_currency:
            print(f"✅ تنسيق العملة: {test_amount} → {formatted_currency}")
        else:
            print(f"❌ تنسيق العملة فشل: {test_amount} → {formatted_currency}")
            all_tests_passed = False
        
        # اختبار تنسيق التاريخ
        test_date = datetime.now()
        date_str, time_str = format_date_thermal(test_date)
        if "/" in date_str and ":" in time_str:
            print(f"✅ تنسيق التاريخ: {date_str} {time_str}")
        else:
            print(f"❌ تنسيق التاريخ فشل: {date_str} {time_str}")
            all_tests_passed = False
            
    except Exception as e:
        print(f"❌ خطأ في الفواتير الحرارية: {e}")
        all_tests_passed = False
    
    print()
    
    # ==================== اختبار 5: فلاتر التطبيق ====================
    print("🌐 اختبار 5: فلاتر التطبيق")
    print("-" * 40)
    
    try:
        from app import convert_to_english_numbers_app, currency_filter, english_numbers_filter
        
        # اختبار فلتر العملة
        test_amount = 5678.90
        currency_result = currency_filter(test_amount)
        if "5,679 د.ج" in currency_result:
            print(f"✅ فلتر العملة: {test_amount} → {currency_result}")
        else:
            print(f"❌ فلتر العملة فشل: {test_amount} → {currency_result}")
            all_tests_passed = False
        
        # اختبار فلتر الأرقام
        arabic_text = "٢٠٢٤-٠١-١٥"
        english_result = english_numbers_filter(arabic_text)
        if english_result == "2024-01-15":
            print(f"✅ فلتر الأرقام: {arabic_text} → {english_result}")
        else:
            print(f"❌ فلتر الأرقام فشل: {arabic_text} → {english_result}")
            all_tests_passed = False
            
    except Exception as e:
        print(f"❌ خطأ في فلاتر التطبيق: {e}")
        all_tests_passed = False
    
    print()
    
    # ==================== اختبار 6: Routes الفواتير ====================
    print("🌐 اختبار 6: Routes الفواتير")
    print("-" * 40)
    
    try:
        from app import app
        
        with app.test_client() as client:
            # فحص الصفحة الرئيسية
            response = client.get('/')
            if response.status_code == 200:
                print("✅ الصفحة الرئيسية تعمل")
            else:
                print(f"❌ الصفحة الرئيسية - كود الخطأ: {response.status_code}")
                all_tests_passed = False
            
            # فحص صفحة المبيعات
            response = client.get('/sales')
            if response.status_code == 200:
                print("✅ صفحة المبيعات تعمل")
            else:
                print(f"❌ صفحة المبيعات - كود الخطأ: {response.status_code}")
                all_tests_passed = False
            
            # فحص صفحة المشتريات
            response = client.get('/purchases')
            if response.status_code == 200:
                print("✅ صفحة المشتريات تعمل")
            else:
                print(f"❌ صفحة المشتريات - كود الخطأ: {response.status_code}")
                all_tests_passed = False
                
    except Exception as e:
        print(f"❌ خطأ في اختبار Routes: {e}")
        all_tests_passed = False
    
    print()
    
    # ==================== النتيجة النهائية ====================
    print("🎯" + "="*60 + "🎯")
    if all_tests_passed:
        print("🎉 جميع الاختبارات نجحت! المشروع جاهز للاستخدام!")
        print()
        print("✅ المميزات المكتملة:")
        print("   🧾 فواتير حرارية احترافية (80mm)")
        print("   📄 فواتير عادية (A4)")
        print("   🔢 أرقام إنجليزية في كل مكان")
        print("   🎨 واجهة محسنة مع أزرار متعددة")
        print("   📊 تصدير Excel للتقارير")
        print()
        print("🚀 للاستخدام:")
        print("   python run_web.py")
        print("   ثم افتح: http://127.0.0.1:5000")
        print()
        print("🧾 للفواتير الحرارية:")
        print("   اضغط الزر الأحمر 🧾 في قوائم المبيعات/المشتريات")
        print()
        print("📄 للفواتير العادية:")
        print("   اضغط الزر الأخضر 📄 في قوائم المبيعات/المشتريات")
        
    else:
        print("❌ بعض الاختبارات فشلت! يرجى مراجعة الأخطاء أعلاه")
        print("💡 تأكد من:")
        print("   • تثبيت جميع المكتبات: pip install -r requirements.txt")
        print("   • وجود جميع الملفات المطلوبة")
        print("   • صحة إعدادات قاعدة البيانات")
    
    print("🎯" + "="*60 + "🎯")
    
    return all_tests_passed

if __name__ == '__main__':
    test_all_features()