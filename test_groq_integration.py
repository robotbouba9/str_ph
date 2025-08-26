#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار تكامل Groq مع التطبيق الرئيسي
"""

import requests
import json
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

def test_groq_integration():
    """اختبار الاتصال مع Groq عبر التطبيق الرئيسي"""
    
    # التحقق من وجود API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ لم يتم العثور على GROQ_API_KEY في ملف .env")
        return False
    
    print(f"✅ تم العثور على GROQ_API_KEY: {api_key[:10]}...")
    
    # اختبار الطلب إلى /ask
    url = "http://localhost:5000/ask"
    data = {
        "message": "مرحبا، كيف يمكنك مساعدتي؟"
    }
    
    try:
        print(f"🔄 إرسال طلب إلى {url}")
        response = requests.post(
            url, 
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 رمز الاستجابة: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ نجح الاتصال!")
            print(f"🤖 رد الذكاء الاصطناعي: {result.get('reply', 'لا يوجد رد')}")
            return True
        else:
            print(f"❌ فشل الطلب: {response.status_code}")
            print(f"📄 محتوى الاستجابة: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ لا يمكن الاتصال بالخادم. تأكد من أن التطبيق يعمل على localhost:5000")
        return False
    except requests.exceptions.Timeout:
        print("❌ انتهت مهلة الطلب")
        return False
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {str(e)}")
        return False

def test_chat_page():
    """اختبار صفحة الدردشة"""
    url = "http://localhost:5000/chat"
    
    try:
        print(f"🔄 اختبار صفحة الدردشة: {url}")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ صفحة الدردشة متاحة")
            return True
        else:
            print(f"❌ فشل في الوصول لصفحة الدردشة: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في اختبار صفحة الدردشة: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 بدء اختبار تكامل Groq")
    print("=" * 50)
    
    # اختبار صفحة الدردشة
    chat_success = test_chat_page()
    print()
    
    # اختبار API
    api_success = test_groq_integration()
    print()
    
    if chat_success and api_success:
        print("🎉 جميع الاختبارات نجحت! التكامل يعمل بشكل صحيح")
    else:
        print("⚠️ بعض الاختبارات فشلت. راجع الأخطاء أعلاه")