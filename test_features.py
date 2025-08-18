#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار المميزات الجديدة
"""

import sys
import os

def test_imports():
    """اختبار استيراد المكتبات الجديدة"""
    print("🧪 اختبار المكتبات الجديدة...")
    print("=" * 40)
    
    try:
        # اختبار reportlab للفواتير الحرارية
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        print("✅ reportlab - فواتير PDF حرارية")
        
        # اختبار openpyxl لتصدير Excel
        import openpyxl
        print("✅ openpyxl - تصدير Excel")
        
        # اختبار weasyprint لتحويل HTML إلى PDF
        try:
            import weasyprint
            print("✅ weasyprint - تحويل HTML إلى PDF")
        except ImportError:
            print("⚠️  weasyprint - غير مثبت (اختياري)")
        
        # اختبار Pillow لمعالجة الصور
        from PIL import Image
        print("✅ Pillow - معالجة الصور")
        
        print("\n🎉 جميع المكتبات الأساسية متوفرة!")
        return True
        
    except ImportError as e:
        print(f"❌ خطأ في استيراد المكتبة: {e}")
        print("\n💡 لتثبيت المكتبات المفقودة:")
        print("pip install -r requirements.txt")
        return False

def test_database_models():
    """اختبار نماذج قاعدة البيانات الجديدة"""
    print("\n🗄️  اختبار نماذج قاعدة البيانات...")
    print("=" * 40)
    
    try:
        from database import PurchaseInvoice, PurchaseItem
        print("✅ PurchaseInvoice - فواتير الشراء")
        print("✅ PurchaseItem - عناصر فواتير الشراء")
        
        # اختبار الفلاتر الجديدة
        from app import currency_filter, currency_decimal_filter
        print("✅ currency_filter - فلتر العملة الجزائرية")
        
        # اختبار قيمة تجريبية
        test_amount = 1234.56
        formatted = currency_filter(test_amount)
        print(f"✅ تنسيق العملة: {test_amount} → {formatted}")
        
        return True
        
    except ImportError as e:
        print(f"❌ خطأ في استيراد النماذج: {e}")
        return False

def test_thermal_invoice():
    """اختبار الفواتير الحرارية المحسنة"""
    print("\n🧾 اختبار الفواتير الحرارية المحسنة...")
    print("=" * 40)
    
    try:
        from thermal_invoice import (ThermalInvoice, format_currency, 
                                   convert_to_english_numbers, format_currency_thermal,
                                   format_date_thermal)
        
        # إنشاء كائن الفاتورة الحرارية
        thermal = ThermalInvoice()
        print("✅ ThermalInvoice - إنشاء الفواتير الحرارية المحسنة")
        
        # اختبار تحويل الأرقام
        arabic_text = "١٢٣٤٥"
        english_text = convert_to_english_numbers(arabic_text)
        print(f"✅ تحويل الأرقام: {arabic_text} → {english_text}")
        
        # اختبار تنسيق العملة
        test_amount = 1500.75
        formatted = format_currency_thermal(test_amount)
        print(f"✅ تنسيق العملة: {test_amount} → {formatted}")
        
        # اختبار تنسيق التاريخ
        from datetime import datetime
        test_date = datetime.now()
        date_str, time_str = format_date_thermal(test_date)
        print(f"✅ تنسيق التاريخ: {date_str} {time_str}")
        
        return True
        
    except ImportError as e:
        print(f"❌ خطأ في استيراد الفواتير الحرارية: {e}")
        return False

def test_excel_export():
    """اختبار تصدير Excel"""
    print("\n📊 اختبار تصدير Excel...")
    print("=" * 40)
    
    try:
        from excel_export import ExcelExporter
        
        # إنشاء كائن التصدير
        exporter = ExcelExporter()
        print("✅ ExcelExporter - تصدير التقارير إلى Excel")
        
        return True
        
    except ImportError as e:
        print(f"❌ خطأ في استيراد تصدير Excel: {e}")
        return False

def main():
    """الاختبار الرئيسي"""
    print("🚀 اختبار المميزات الجديدة لمتجر الهواتف")
    print("=" * 50)
    
    all_tests_passed = True
    
    # اختبار المكتبات
    if not test_imports():
        all_tests_passed = False
    
    # اختبار قاعدة البيانات
    if not test_database_models():
        all_tests_passed = False
    
    # اختبار الفواتير الحرارية
    if not test_thermal_invoice():
        all_tests_passed = False
    
    # اختبار تصدير Excel
    if not test_excel_export():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 جميع الاختبارات نجحت! المشروع جاهز للاستخدام")
        print("\n🚀 لتشغيل التطبيق:")
        print("python run_web.py")
        print("\n📋 المميزات الجديدة المتاحة:")
        print("• فواتير حرارية احترافية (80mm)")
        print("• تصدير Excel للتقارير")
        print("• العملة الجزائرية (د.ج)")
        print("• فواتير الموردين مع تحديث المخزون")
        print("• تقارير متقدمة مع فلاتر التاريخ")
    else:
        print("❌ بعض الاختبارات فشلت!")
        print("💡 تأكد من تثبيت جميع المتطلبات:")
        print("pip install -r requirements.txt")

if __name__ == '__main__':
    main()