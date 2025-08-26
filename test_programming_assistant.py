#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار المساعد البرمجي الذكي
"""

import requests
import json

def test_chat():
    """اختبار الدردشة البرمجية"""
    print("🔄 اختبار الدردشة البرمجية...")
    
    questions = [
        "ما هي الملفات الرئيسية في هذا المشروع؟",
        "كيف يعمل نظام المبيعات في التطبيق؟",
        "ما هي أفضل طريقة لتحسين أداء قاعدة البيانات؟",
        "كيف يمكنني إضافة ميزة جديدة للتطبيق؟"
    ]
    
    for question in questions:
        try:
            response = requests.post(
                "http://localhost:8000/ask",
                json={"message": question},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ سؤال: {question}")
                print(f"🤖 الجواب: {data['reply'][:100]}...")
                print("-" * 50)
            else:
                print(f"❌ فشل السؤال: {question}")
                
        except Exception as e:
            print(f"❌ خطأ في السؤال: {question} - {e}")
    
    return True

def test_code_analysis():
    """اختبار تحليل الكود"""
    print("🔄 اختبار تحليل الكود...")
    
    # كود Python بسيط للاختبار
    test_code = '''
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price'] * item['quantity']
    return total

# استخدام الدالة
products = [
    {'name': 'iPhone', 'price': 1000, 'quantity': 2},
    {'name': 'Samsung', 'price': 800, 'quantity': 1}
]
result = calculate_total(products)
print(result)
'''
    
    analysis_types = ['general', 'security', 'performance', 'structure']
    
    for analysis_type in analysis_types:
        try:
            response = requests.post(
                "http://localhost:8000/analyze",
                json={
                    "code": test_code,
                    "type": analysis_type
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ تحليل {analysis_type}:")
                print(f"📊 النتيجة: {data['analysis'][:150]}...")
                print("-" * 50)
            else:
                print(f"❌ فشل تحليل {analysis_type}")
                
        except Exception as e:
            print(f"❌ خطأ في تحليل {analysis_type}: {e}")
    
    return True

def test_health():
    """اختبار حالة الخادم"""
    print("🔄 اختبار حالة الخادم...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ الخادم يعمل: {data}")
            return True
        else:
            print(f"❌ مشكلة في الخادم: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ لا يمكن الاتصال بالخادم: {e}")
        return False

def main():
    print("🚀 اختبار المساعد البرمجي الذكي")
    print("=" * 60)
    
    # اختبار حالة الخادم
    if not test_health():
        print("⚠️ الخادم لا يعمل. تأكد من تشغيل: python groq_server.py")
        return
    
    print()
    
    # اختبار الدردشة
    test_chat()
    print()
    
    # اختبار تحليل الكود
    test_code_analysis()
    
    print("🎉 انتهى الاختبار!")
    print("\n💡 لفتح الواجهة:")
    print("- افتح المتصفح على: http://localhost:8000")
    print("- أو افتح ملف static/index.html مباشرة")

if __name__ == "__main__":
    main()