#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار خادم Groq المنفصل
"""

import requests
import json
import webbrowser
import os

def test_groq_server():
    """اختبار خادم Groq المنفصل"""
    
    print("🚀 اختبار خادم Groq المنفصل")
    print("=" * 50)
    
    # اختبار حالة الخادم
    try:
        print("🔄 اختبار حالة الخادم...")
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ الخادم يعمل: {health_data}")
        else:
            print(f"❌ مشكلة في الخادم: {health_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ لا يمكن الاتصال بالخادم: {e}")
        return False
    
    # اختبار API
    try:
        print("🔄 اختبار API...")
        api_response = requests.post(
            "http://localhost:8000/ask",
            json={"message": "مرحبا، ما هي أفضل الهواتف المتاحة؟"},
            timeout=30
        )
        
        if api_response.status_code == 200:
            data = api_response.json()
            print(f"✅ API يعمل بنجاح!")
            print(f"🤖 رد الذكاء الاصطناعي: {data.get('reply', 'لا يوجد رد')}")
        else:
            print(f"❌ مشكلة في API: {api_response.status_code}")
            print(f"📄 الاستجابة: {api_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في اختبار API: {e}")
        return False
    
    return True

def open_chat_page():
    """فتح صفحة الدردشة في المتصفح"""
    try:
        # فتح الصفحة من الخادم
        print("🌐 فتح صفحة الدردشة من الخادم...")
        webbrowser.open("http://localhost:8000")
        
        # فتح الملف مباشرة أيضاً للمقارنة
        print("📁 فتح الملف مباشرة...")
        file_path = os.path.abspath("static/index.html")
        webbrowser.open(f"file://{file_path}")
        
        print("✅ تم فتح الصفحات في المتصفح")
        return True
    except Exception as e:
        print(f"❌ خطأ في فتح المتصفح: {e}")
        return False

if __name__ == "__main__":
    # اختبار الخادم
    if test_groq_server():
        print("\n🎉 جميع الاختبارات نجحت!")
        
        # سؤال المستخدم إذا كان يريد فتح المتصفح
        response = input("\n❓ هل تريد فتح صفحة الدردشة في المتصفح؟ (y/n): ")
        if response.lower() in ['y', 'yes', 'نعم', 'ن']:
            open_chat_page()
            print("\n📋 تعليمات:")
            print("1. الصفحة الأولى: من الخادم (http://localhost:8000)")
            print("2. الصفحة الثانية: ملف HTML مباشر")
            print("3. كلاهما يجب أن يتصل بـ Groq بنجاح")
    else:
        print("\n⚠️ فشل في الاختبار. تأكد من تشغيل الخادم أولاً:")
        print("python groq_server.py")