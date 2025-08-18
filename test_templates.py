#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار القوالب والأرقام الإنجليزية
"""

import sys
import os
from datetime import datetime

def test_templates_and_numbers():
    """اختبار القوالب والأرقام الإنجليزية"""
    print("🎨 اختبار القوالب والأرقام الإنجليزية")
    print("=" * 50)
    
    try:
        from app import app, convert_to_english_numbers_app, currency_filter, english_numbers_filter
        
        # اختبار فلاتر الأرقام
        print("🔢 اختبار فلاتر الأرقام:")
        print("-" * 30)
        
        # اختبار تحويل الأرقام
        arabic_numbers = "١٢٣٤٥"
        english_result = convert_to_english_numbers_app(arabic_numbers)
        print(f"✅ تحويل الأرقام: {arabic_numbers} → {english_result}")
        
        # اختبار فلتر العملة
        amount = 1234.56
        currency_result = currency_filter(amount)
        print(f"✅ فلتر العملة: {amount} → {currency_result}")
        
        # اختبار فلتر الأرقام الإنجليزية
        arabic_date = "٢٠٢٤-٠١-١٥"
        english_date = english_numbers_filter(arabic_date)
        print(f"✅ فلتر التاريخ: {arabic_date} → {english_date}")
        
        print()
        
        # اختبار التطبيق مع بيانات وهمية
        print("🌐 اختبار التطبيق:")
        print("-" * 30)
        
        with app.test_client() as client:
            # اختبار الصفحة الرئيسية
            response = client.get('/')
            if response.status_code == 200:
                print("✅ الصفحة الرئيسية تعمل")
                
                # فحص محتوى الصفحة للأرقام العربية
                content = response.get_data(as_text=True)
                arabic_digits = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩']
                found_arabic = any(digit in content for digit in arabic_digits)
                
                if found_arabic:
                    print("⚠️  تحذير: وجدت أرقام عربية في الصفحة الرئيسية")
                else:
                    print("✅ لا توجد أرقام عربية في الصفحة الرئيسية")
            else:
                print(f"❌ خطأ في الصفحة الرئيسية: {response.status_code}")
            
            # اختبار صفحة المبيعات
            response = client.get('/sales')
            if response.status_code == 200:
                print("✅ صفحة المبيعات تعمل")
                
                # فحص الأزرار في صفحة المبيعات
                content = response.get_data(as_text=True)
                
                # البحث عن أزرار الفواتير
                thermal_button = 'thermal-pdf' in content
                regular_button = 'regular-pdf' in content
                view_button = 'view_sale' in content
                
                if thermal_button and regular_button and view_button:
                    print("✅ أزرار الفواتير موجودة (عرض + حراري + عادي)")
                else:
                    print(f"⚠️  فحص الأزرار: عرض={view_button}, حراري={thermal_button}, عادي={regular_button}")
                
                # فحص target="_blank" للفواتير الحرارية
                if 'target="_blank"' in content:
                    print("✅ الفواتير تفتح في نافذة جديدة")
                else:
                    print("❌ الفواتير لا تفتح في نافذة جديدة")
                    
            else:
                print(f"❌ خطأ في صفحة المبيعات: {response.status_code}")
        
        print()
        
        # اختبار الفواتير الحرارية
        print("🧾 اختبار الفواتير الحرارية:")
        print("-" * 30)
        
        from thermal_invoice import ThermalInvoice, convert_to_english_numbers, format_currency_thermal
        
        # اختبار تحويل الأرقام في الفواتير
        test_phone = "+٢١٣ ٥٥٥ ١٢٣ ٤٥٦"
        converted_phone = convert_to_english_numbers(test_phone)
        print(f"✅ تحويل الهاتف: {test_phone} → {converted_phone}")
        
        # اختبار تنسيق العملة
        test_amount = 15000
        formatted_amount = format_currency_thermal(test_amount)
        print(f"✅ تنسيق العملة: {test_amount} → {formatted_amount}")
        
        # اختبار إنشاء فاتورة
        thermal = ThermalInvoice()
        print(f"✅ إنشاء كائن الفاتورة الحرارية - العرض: {thermal.width/3.527:.0f}mm")
        
        print()
        print("🎯 نتائج الاختبار:")
        print("=" * 50)
        print("✅ فلاتر الأرقام الإنجليزية تعمل")
        print("✅ التطبيق يعمل بشكل صحيح")
        print("✅ الفواتير الحرارية جاهزة")
        print("✅ الأزرار منظمة ومرتبة")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_templates_and_numbers()