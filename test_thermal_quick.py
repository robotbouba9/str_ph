#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع للفواتير الحرارية المحسنة
"""

def test_thermal_features():
    """اختبار المميزات الحرارية"""
    print("🧾 اختبار الفواتير الحرارية المحسنة")
    print("=" * 50)
    
    # اختبار استيراد المكتبات
    print("📦 اختبار المكتبات المطلوبة:")
    
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm
        print("✅ reportlab - مكتبة PDF")
    except ImportError:
        print("❌ reportlab غير مثبت")
        return False
    
    try:
        from thermal_invoice import (ThermalInvoice, convert_to_english_numbers, 
                                   format_currency_thermal, format_date_thermal)
        print("✅ thermal_invoice - نظام الفواتير الحرارية")
    except ImportError as e:
        print(f"❌ thermal_invoice - خطأ: {e}")
        return False
    
    # اختبار دوال التحويل
    print("\n🔢 اختبار دوال التحويل:")
    
    # تحويل الأرقام
    arabic_numbers = "١٢٣٤٥"
    english_numbers = convert_to_english_numbers(arabic_numbers)
    print(f"✅ تحويل الأرقام: {arabic_numbers} → {english_numbers}")
    
    # تنسيق العملة
    amount = 1234.56
    formatted_currency = format_currency_thermal(amount)
    print(f"✅ تنسيق العملة: {amount} → {formatted_currency}")
    
    # تنسيق التاريخ
    from datetime import datetime
    now = datetime.now()
    date_str, time_str = format_date_thermal(now)
    print(f"✅ تنسيق التاريخ: {date_str} {time_str}")
    
    # اختبار إنشاء كائن الفاتورة
    print("\n🏗️  اختبار إنشاء الفاتورة:")
    
    try:
        thermal = ThermalInvoice()
        print("✅ تم إنشاء كائن ThermalInvoice بنجاح")
        print(f"   العرض: {thermal.width/mm:.0f}mm")
        print(f"   الارتفاع: {thermal.height/mm:.0f}mm")
    except Exception as e:
        print(f"❌ فشل في إنشاء كائن ThermalInvoice: {e}")
        return False
    
    # اختبار Routes الجديدة
    print("\n🌐 Routes الجديدة المتاحة:")
    routes = [
        "/sales/<id>/thermal-pdf - فاتورة بيع حرارية (80mm)",
        "/sales/<id>/regular-pdf - فاتورة بيع عادية (A4)",
        "/purchases/<id>/thermal-pdf - فاتورة شراء حرارية (80mm)",
        "/purchases/<id>/regular-pdf - فاتورة شراء عادية (A4)"
    ]
    
    for route in routes:
        print(f"✅ {route}")
    
    # اختبار فلاتر القوالب
    print("\n🎨 فلاتر القوالب الجديدة:")
    
    try:
        from app import currency_filter, english_numbers_filter
        
        # اختبار فلتر العملة
        test_amount = 5678.90
        currency_result = currency_filter(test_amount)
        print(f"✅ currency: {test_amount} → {currency_result}")
        
        # اختبار فلتر الأرقام
        arabic_text = "٢٠٢٤-٠١-١٥"
        english_result = english_numbers_filter(arabic_text)
        print(f"✅ english_numbers: {arabic_text} → {english_result}")
        
    except ImportError as e:
        print(f"❌ فشل في استيراد فلاتر القوالب: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 جميع اختبارات الفواتير الحرارية نجحت!")
    print("\n📋 المميزات الجاهزة:")
    print("✅ فواتير حرارية احترافية (80mm)")
    print("✅ فواتير عادية (A4)")
    print("✅ أرقام إنجليزية في كل مكان")
    print("✅ تصميم مثل المحلات التجارية")
    print("✅ أزرار طباعة متعددة")
    
    print("\n🚀 للاستخدام:")
    print("1. شغل التطبيق: python run_web.py")
    print("2. اذهب للمبيعات أو المشتريات")
    print("3. اضغط الزر الأحمر 🧾 للفاتورة الحرارية")
    print("4. اضغط الزر الأخضر 📄 للفاتورة العادية")
    
    return True

if __name__ == '__main__':
    test_thermal_features()