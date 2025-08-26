#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار المساعد البرمجي المحسن مع إدارة الملفات والـ Terminal
"""

import requests
import json
import webbrowser
import time

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

def test_chat_with_commands():
    """اختبار الدردشة مع الأوامر الخاصة"""
    print("🔄 اختبار الدردشة مع الأوامر الخاصة...")
    
    commands = [
        "اعرض ملفات",
        "اقرأ ملف app.py",
        "نفذ أمر dir",
        "ما هي الملفات الرئيسية في المشروع؟"
    ]
    
    for command in commands:
        try:
            response = requests.post(
                "http://localhost:8000/ask",
                json={"message": command},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ أمر: {command}")
                print(f"🤖 الرد: {data['reply'][:100]}...")
                print("-" * 50)
            else:
                print(f"❌ فشل الأمر: {command}")
                
        except Exception as e:
            print(f"❌ خطأ في الأمر: {command} - {e}")
    
    return True

def test_file_management():
    """اختبار إدارة الملفات"""
    print("🔄 اختبار إدارة الملفات...")
    
    # اختبار عرض الملفات
    try:
        response = requests.get("http://localhost:8000/files")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ عرض الملفات: وُجد {len(data['files'])} ملف/مجلد")
        else:
            print(f"❌ فشل عرض الملفات: {response.status_code}")
    except Exception as e:
        print(f"❌ خطأ في عرض الملفات: {e}")
    
    # اختبار قراءة ملف
    try:
        response = requests.get("http://localhost:8000/file?path=app.py")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ قراءة ملف app.py: {len(data['content'])} حرف")
        else:
            print(f"❌ فشل قراءة الملف: {response.status_code}")
    except Exception as e:
        print(f"❌ خطأ في قراءة الملف: {e}")
    
    # اختبار إنشاء ملف تجريبي
    test_content = "# ملف تجريبي\nprint('مرحبا من المساعد البرمجي!')"
    try:
        response = requests.post(
            "http://localhost:8000/file",
            json={"path": "test_file.py", "content": test_content}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ إنشاء ملف تجريبي: {data['message']}")
        else:
            print(f"❌ فشل إنشاء الملف: {response.status_code}")
    except Exception as e:
        print(f"❌ خطأ في إنشاء الملف: {e}")
    
    return True

def test_terminal():
    """اختبار Terminal"""
    print("🔄 اختبار Terminal...")
    
    commands = [
        "echo Hello World",
        "python --version",
        "dir",
        "whoami"
    ]
    
    for command in commands:
        try:
            response = requests.post(
                "http://localhost:8000/execute",
                json={"command": command}
            )
            
            if response.status_code == 200:
                data = response.json()
                status = "✅" if data["success"] else "❌"
                print(f"{status} أمر: {command}")
                if data["output"]:
                    print(f"📤 المخرجات: {data['output'][:50]}...")
                if data["error"]:
                    print(f"⚠️ أخطاء: {data['error'][:50]}...")
                print("-" * 30)
            else:
                print(f"❌ فشل الأمر: {command}")
                
        except Exception as e:
            print(f"❌ خطأ في الأمر: {command} - {e}")
    
    return True

def test_code_analysis():
    """اختبار تحليل الكود"""
    print("🔄 اختبار تحليل الكود...")
    
    test_code = '''
def process_sale(product_id, quantity, customer_id):
    # بدون تحقق من المدخلات
    product = Product.query.get(product_id)
    total = product.price * quantity
    
    # بدون معالجة الأخطاء
    sale = Sale(
        product_id=product_id,
        quantity=quantity,
        customer_id=customer_id,
        total=total
    )
    db.session.add(sale)
    db.session.commit()
    return sale
'''
    
    analysis_types = ['security', 'performance']
    
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
                print(f"📊 النتيجة: {data['analysis'][:100]}...")
                print("-" * 50)
            else:
                print(f"❌ فشل تحليل {analysis_type}")
                
        except Exception as e:
            print(f"❌ خطأ في تحليل {analysis_type}: {e}")
    
    return True

def open_interface():
    """فتح الواجهة في المتصفح"""
    try:
        print("🌐 فتح الواجهة في المتصفح...")
        webbrowser.open("http://localhost:8000")
        return True
    except Exception as e:
        print(f"❌ خطأ في فتح المتصفح: {e}")
        return False

def main():
    print("🚀 اختبار المساعد البرمجي المحسن")
    print("=" * 60)
    
    # اختبار حالة الخادم
    if not test_health():
        print("⚠️ الخادم لا يعمل. تأكد من تشغيل: python groq_server.py")
        return
    
    print()
    
    # اختبار الدردشة مع الأوامر
    test_chat_with_commands()
    print()
    
    # اختبار إدارة الملفات
    test_file_management()
    print()
    
    # اختبار Terminal
    test_terminal()
    print()
    
    # اختبار تحليل الكود
    test_code_analysis()
    
    print("🎉 انتهى الاختبار!")
    print("\n💡 الميزات المتاحة:")
    print("✅ دردشة ذكية مع أوامر خاصة")
    print("✅ إدارة الملفات (قراءة/كتابة/إنشاء)")
    print("✅ Terminal متكامل")
    print("✅ تحليل الكود المتقدم")
    print("✅ واجهة احترافية بـ 4 تبويبات")
    
    # سؤال المستخدم إذا كان يريد فتح الواجهة
    response = input("\n❓ هل تريد فتح الواجهة في المتصفح؟ (y/n): ")
    if response.lower() in ['y', 'yes', 'نعم', 'ن']:
        open_interface()
        print("\n🎊 المساعد البرمجي جاهز للاستخدام!")
        print("📋 جرب الميزات التالية:")
        print("- 💬 الدردشة: اسأل 'اعرض ملفات' أو 'اقرأ ملف app.py'")
        print("- 🔍 تحليل الكود: ارفع ملف أو الصق كود")
        print("- 📁 إدارة الملفات: تصفح وعدل الملفات")
        print("- 💻 Terminal: نفذ أوامر النظام")

if __name__ == "__main__":
    main()