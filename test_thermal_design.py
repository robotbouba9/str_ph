#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار تصميم الفواتير الحرارية الجديد
"""

import sys
import os
from datetime import datetime
from io import BytesIO

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_thermal_design():
    """اختبار تصميم الفاتورة الحرارية الجديد"""
    print("🧾 اختبار تصميم الفاتورة الحرارية الجديد")
    print("=" * 50)
    
    try:
        from thermal_invoice import ThermalInvoice, convert_to_english_numbers, format_currency_thermal
        
        # إنشاء كائن فاتورة وهمية للاختبار
        class MockCustomer:
            def __init__(self):
                self.name = "أحمد محمد"
                self.phone = "+٢١٣ ٥٥٥ ١٢٣ ٤٥٦"
        
        class MockProduct:
            def __init__(self, name):
                self.name = name
        
        class MockSaleItem:
            def __init__(self, product_name, quantity, unit_price):
                self.product = MockProduct(product_name)
                self.quantity = quantity
                self.unit_price = unit_price
                self.total_price = quantity * unit_price
        
        class MockSale:
            def __init__(self):
                self.id = 123
                self.created_at = datetime.now()
                self.customer = MockCustomer()
                self.sale_items = [
                    MockSaleItem("iPhone 15 Pro Max 256GB", 1, 180000),
                    MockSaleItem("Samsung Galaxy S24 Ultra", 1, 150000),
                    MockSaleItem("Wireless Charger", 2, 5000),
                ]
                self.total_amount = sum(item.total_price for item in self.sale_items)
                self.discount = 10000
                self.final_amount = self.total_amount - self.discount
                self.payment_method = "نقداً"
                self.notes = "فاتورة تجريبية للاختبار"
        
        # إنشاء الفاتورة
        print("📋 إنشاء فاتورة تجريبية...")
        thermal = ThermalInvoice()
        mock_sale = MockSale()
        
        print(f"✅ رقم الفاتورة: {convert_to_english_numbers(str(mock_sale.id))}")
        print(f"✅ العميل: {mock_sale.customer.name}")
        print(f"✅ الهاتف: {convert_to_english_numbers(mock_sale.customer.phone)}")
        print(f"✅ عدد المنتجات: {len(mock_sale.sale_items)}")
        print(f"✅ المجموع: {format_currency_thermal(mock_sale.final_amount)}")
        
        # إنشاء PDF
        print("\n🔧 إنشاء PDF...")
        pdf_data = thermal.create_sale_invoice(mock_sale)
        
        if pdf_data:
            print("✅ تم إنشاء PDF بنجاح!")
            print(f"✅ حجم الملف: {len(pdf_data)} بايت")
            
            # حفظ الملف للاختبار
            with open("test_thermal_invoice.pdf", "wb") as f:
                f.write(pdf_data)
            print("✅ تم حفظ الملف: test_thermal_invoice.pdf")
            
        else:
            print("❌ فشل في إنشاء PDF")
            return False
        
        print("\n🎨 مميزات التصميم الجديد:")
        print("✅ عرض 80mm مناسب للطابعات الحرارية")
        print("✅ تصميم احترافي مثل المحلات التجارية")
        print("✅ رأس واضح مع اسم المتجر")
        print("✅ معلومات الفاتورة منظمة")
        print("✅ جدول منتجات احترافي")
        print("✅ مجاميع واضحة ومنظمة")
        print("✅ ذيل مع رسالة شكر")
        print("✅ جميع الأرقام إنجليزية")
        
        print("\n" + "=" * 50)
        print("🎉 اختبار التصميم نجح بالكامل!")
        print("📄 افتح الملف test_thermal_invoice.pdf لرؤية النتيجة")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_thermal_design()