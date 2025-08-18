#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
التحقق النهائي من جميع المتطلبات
"""

import sys
import os
from datetime import datetime

def final_verification():
    """التحقق النهائي من جميع المتطلبات"""
    print("🎯" + "="*60 + "🎯")
    print("🏪          التحقق النهائي من المشروع          🏪")
    print("🎯" + "="*60 + "🎯")
    print()
    
    all_requirements_met = True
    
    # ==================== 1. الفواتير الحرارية ====================
    print("🧾 1. اختبار الفواتير الحرارية:")
    print("-" * 40)
    
    try:
        from thermal_invoice import ThermalInvoice, convert_to_english_numbers, format_currency_thermal, format_date_thermal
        
        # اختبار التصميم
        thermal = ThermalInvoice()
        width_mm = thermal.width * 25.4 / 72  # تحويل صحيح من نقطة إلى مم
        
        if abs(width_mm - 80) < 5:  # تسامح 5 مم
            print(f"✅ عرض الفاتورة: {width_mm:.0f}mm (مناسب للطابعات الحرارية)")
        else:
            print(f"❌ عرض الفاتورة: {width_mm:.0f}mm (غير مناسب)")
            all_requirements_met = False
        
        # اختبار تحويل الأرقام
        test_cases = [
            ("١٢٣٤٥", "12345"),
            ("+٢١٣ ٥٥٥ ١٢٣ ٤٥٦", "+213 555 123 456"),
            ("٢٠٢٤-٠١-١٥", "2024-01-15")
        ]
        
        for arabic, expected in test_cases:
            result = convert_to_english_numbers(arabic)
            if result == expected:
                print(f"✅ تحويل الأرقام: {arabic} → {result}")
            else:
                print(f"❌ تحويل الأرقام فشل: {arabic} → {result} (متوقع: {expected})")
                all_requirements_met = False
        
        # اختبار تنسيق العملة
        amount = 15000
        currency_result = format_currency_thermal(amount)
        if "15,000 DA" in currency_result:
            print(f"✅ تنسيق العملة: {amount} → {currency_result}")
        else:
            print(f"❌ تنسيق العملة فشل: {amount} → {currency_result}")
            all_requirements_met = False
        
        # اختبار تنسيق التاريخ
        test_date = datetime.now()
        date_str, time_str = format_date_thermal(test_date)
        if "/" in date_str and ":" in time_str:
            print(f"✅ تنسيق التاريخ: {date_str} {time_str}")
        else:
            print(f"❌ تنسيق التاريخ فشل: {date_str} {time_str}")
            all_requirements_met = False
            
    except Exception as e:
        print(f"❌ خطأ في الفواتير الحرارية: {e}")
        all_requirements_met = False
    
    print()
    
    # ==================== 2. فلاتر التطبيق ====================
    print("🌐 2. اختبار فلاتر التطبيق:")
    print("-" * 40)
    
    try:
        from app import convert_to_english_numbers_app, currency_filter, english_numbers_filter
        
        # اختبار فلتر العملة
        test_amount = 1234.56
        currency_result = currency_filter(test_amount)
        if "1,235 د.ج" in currency_result:
            print(f"✅ فلتر العملة: {test_amount} → {currency_result}")
        else:
            print(f"❌ فلتر العملة فشل: {test_amount} → {currency_result}")
            all_requirements_met = False
        
        # اختبار فلتر الأرقام الإنجليزية
        arabic_text = "٢٠٢٤-٠١-١٥"
        english_result = english_numbers_filter(arabic_text)
        if english_result == "2024-01-15":
            print(f"✅ فلتر الأرقام: {arabic_text} → {english_result}")
        else:
            print(f"❌ فلتر الأرقام فشل: {arabic_text} → {english_result}")
            all_requirements_met = False
            
    except Exception as e:
        print(f"❌ خطأ في فلاتر التطبيق: {e}")
        all_requirements_met = False
    
    print()
    
    # ==================== 3. Routes والاستجابات ====================
    print("🌐 3. اختبار Routes والاستجابات:")
    print("-" * 40)
    
    try:
        from app import app
        
        with app.test_client() as client:
            # اختبار الصفحة الرئيسية
            response = client.get('/')
            if response.status_code == 200:
                print("✅ الصفحة الرئيسية تعمل")
            else:
                print(f"❌ الصفحة الرئيسية - خطأ: {response.status_code}")
                all_requirements_met = False
            
            # اختبار صفحة المبيعات
            response = client.get('/sales')
            if response.status_code == 200:
                print("✅ صفحة المبيعات تعمل")
                
                # فحص الأزرار
                content = response.get_data(as_text=True)
                thermal_button = 'thermal-pdf' in content
                regular_button = 'regular-pdf' in content
                target_blank = 'target="_blank"' in content
                
                if thermal_button and regular_button:
                    print("✅ أزرار الفواتير موجودة")
                else:
                    print("❌ أزرار الفواتير مفقودة")
                    all_requirements_met = False
                
                if target_blank:
                    print("✅ الفواتير تفتح في نافذة جديدة")
                else:
                    print("❌ الفواتير لا تفتح في نافذة جديدة")
                    all_requirements_met = False
                    
            else:
                print(f"❌ صفحة المبيعات - خطأ: {response.status_code}")
                all_requirements_met = False
            
            # اختبار صفحة المشتريات
            response = client.get('/purchases')
            if response.status_code == 200:
                print("✅ صفحة المشتريات تعمل")
            else:
                print(f"❌ صفحة المشتريات - خطأ: {response.status_code}")
                all_requirements_met = False
                
    except Exception as e:
        print(f"❌ خطأ في اختبار Routes: {e}")
        all_requirements_met = False
    
    print()
    
    # ==================== 4. اختبار إنشاء فاتورة حقيقية ====================
    print("🧾 4. اختبار إنشاء فاتورة حقيقية:")
    print("-" * 40)
    
    try:
        from app import app
        from database import Sale
        
        with app.app_context():
            sale = Sale.query.first()
            
            if sale:
                print(f"✅ وجدت مبيعة للاختبار - ID: {sale.id}")
                
                # اختبار إنشاء الفاتورة الحرارية
                thermal = ThermalInvoice()
                pdf_data = thermal.create_sale_invoice(sale)
                
                if pdf_data and len(pdf_data) > 1000:  # حجم معقول للـ PDF
                    print(f"✅ تم إنشاء الفاتورة الحرارية - الحجم: {len(pdf_data)} بايت")
                    
                    # حفظ الفاتورة للفحص اليدوي
                    with open("final_test_thermal.pdf", "wb") as f:
                        f.write(pdf_data)
                    print("✅ تم حفظ الفاتورة: final_test_thermal.pdf")
                    
                else:
                    print("❌ فشل في إنشاء الفاتورة الحرارية")
                    all_requirements_met = False
                    
            else:
                print("⚠️  لا توجد مبيعات للاختبار")
                
    except Exception as e:
        print(f"❌ خطأ في اختبار الفاتورة: {e}")
        all_requirements_met = False
    
    print()
    
    # ==================== 5. فحص الملفات المطلوبة ====================
    print("📁 5. فحص الملفات المطلوبة:")
    print("-" * 40)
    
    required_files = [
        ('app.py', 'ملف التطبيق الرئيسي'),
        ('thermal_invoice.py', 'نظام الفواتير الحرارية'),
        ('database.py', 'قاعدة البيانات'),
        ('run_web.py', 'ملف التشغيل'),
        ('templates/sales.html', 'قالب المبيعات'),
        ('templates/purchases.html', 'قالب المشتريات'),
        ('requirements.txt', 'متطلبات المشروع')
    ]
    
    for file_path, description in required_files:
        if os.path.exists(file_path):
            print(f"✅ {description}")
        else:
            print(f"❌ {description} - مفقود: {file_path}")
            all_requirements_met = False
    
    print()
    
    # ==================== النتيجة النهائية ====================
    print("🎯" + "="*60 + "🎯")
    
    if all_requirements_met:
        print("🎉 جميع المتطلبات تم تنفيذها بنجاح!")
        print()
        print("✅ المميزات المكتملة:")
        print("   🧾 فواتير حرارية احترافية (80mm)")
        print("   🔢 أرقام إنجليزية في كل مكان")
        print("   📄 طباعة متعددة (حراري + عادي)")
        print("   🎨 واجهة محسنة مع أزرار منظمة")
        print("   🌐 فتح الفواتير في نافذة جديدة")
        print()
        print("🚀 المشروع جاهز للاستخدام التجاري!")
        print("🌐 للتشغيل: python run_web.py")
        print("🌐 الوصول: http://127.0.0.1:5000")
        
    else:
        print("❌ بعض المتطلبات لم تكتمل!")
        print("💡 يرجى مراجعة الأخطاء أعلاه وإصلاحها")
    
    print("🎯" + "="*60 + "🎯")
    
    return all_requirements_met

if __name__ == '__main__':
    final_verification()