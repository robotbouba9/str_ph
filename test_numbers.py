#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع لتحويل الأرقام العربية إلى إنجليزية
"""

def test_number_conversion():
    """اختبار تحويل الأرقام"""
    print("🔢 اختبار تحويل الأرقام العربية إلى إنجليزية")
    print("=" * 50)
    
    # استيراد دالة التحويل
    try:
        from thermal_invoice import convert_to_english_numbers
        print("✅ تم استيراد دالة التحويل بنجاح")
    except ImportError:
        print("❌ فشل في استيراد دالة التحويل")
        return False
    
    # اختبارات مختلفة
    test_cases = [
        ("١٢٣٤٥", "12345", "أرقام عربية بسيطة"),
        ("٢٠٢٤-٠١-١٥", "2024-01-15", "تاريخ"),
        ("١٤:٣٠", "14:30", "وقت"),
        ("١,٢٣٤ د.ج", "1,234 د.ج", "عملة"),
        ("+٢١٣ ١٢٣ ٤٥٦ ٧٨٩", "+213 123 456 789", "رقم هاتف"),
        ("PUR-٠٠٠٠٠١", "PUR-000001", "رقم فاتورة"),
        ("الكمية: ٥ قطع", "الكمية: 5 قطع", "نص مختلط"),
        ("", "", "نص فارغ"),
        (None, "", "قيمة None"),
        ("123", "123", "أرقام إنجليزية (بدون تغيير)"),
    ]
    
    print("\n📋 نتائج الاختبارات:")
    print("-" * 50)
    
    all_passed = True
    
    for i, (input_text, expected, description) in enumerate(test_cases, 1):
        try:
            result = convert_to_english_numbers(input_text)
            
            if result == expected:
                print(f"✅ اختبار {i}: {description}")
                print(f"   المدخل: '{input_text}' → النتيجة: '{result}'")
            else:
                print(f"❌ اختبار {i}: {description}")
                print(f"   المدخل: '{input_text}'")
                print(f"   المتوقع: '{expected}'")
                print(f"   الفعلي: '{result}'")
                all_passed = False
                
        except Exception as e:
            print(f"❌ اختبار {i}: {description} - خطأ: {e}")
            all_passed = False
        
        print()
    
    # اختبار فلاتر التطبيق
    print("🌐 اختبار فلاتر التطبيق:")
    print("-" * 30)
    
    try:
        from app import convert_to_english_numbers_app, currency_filter
        
        # اختبار فلتر العملة
        test_amount = 1234.56
        currency_result = currency_filter(test_amount)
        print(f"✅ فلتر العملة: {test_amount} → {currency_result}")
        
        # اختبار فلتر الأرقام
        arabic_text = "١٢٣٤"
        english_result = convert_to_english_numbers_app(arabic_text)
        print(f"✅ فلتر الأرقام: {arabic_text} → {english_result}")
        
    except ImportError as e:
        print(f"❌ فشل في استيراد فلاتر التطبيق: {e}")
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 جميع اختبارات تحويل الأرقام نجحت!")
        print("✅ الأرقام العربية ستظهر كأرقام إنجليزية في:")
        print("   • التواريخ والأوقات")
        print("   • الأسعار والعملات")
        print("   • أرقام الهواتف")
        print("   • أرقام الفواتير")
        print("   • الكميات والإحصائيات")
    else:
        print("❌ بعض اختبارات تحويل الأرقام فشلت!")
        print("💡 تحقق من دوال التحويل في الملفات")
    
    return all_passed

if __name__ == '__main__':
    test_number_conversion()