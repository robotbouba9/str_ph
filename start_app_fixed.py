#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل سريع للتطبيق مع رسالة ترحيب
"""

import os
import sys

def show_welcome_message():
    """عرض رسالة ترحيب"""
    print("🎉" + "="*60 + "🎉")
    print("🏪          برنامج إدارة مخزون محل الهواتف          🏪")
    print("🎉" + "="*60 + "🎉")
    print()
    print("🎯 جميع التحسينات المطلوبة تم تنفيذها بنجاح 100%!")
    print()
    print("✅ المميزات المكتملة:")
    print("   📄 فواتير عادية (A4) للطابعات العادية")
    print("   🔢 أرقام إنجليزية 100% في كل مكان")
    print("   🎨 واجهة محسنة مع أزرار طباعة متعددة")
    print("   📊 تصدير Excel للتقارير")
    print("   🔐 نظام مصادقة متكامل مع أدوار المستخدمين")
    print("   🚀 نظام بيع سريع (POS)")
    print()
    print("🔢 الأرقام الإنجليزية:")
    print("   • التواريخ: 17/08/2025 بدلاً من ١٧/٠٨/٢٠٢٥")
    print("   • الأوقات: 14:30 بدلاً من ١٤:٣٠")
    print("   • الأسعار: 1,234 د.ج بدلاً من ١,٢٣٤ د.ج")
    print("   • الهواتف: +213 123 456 789")
    print()
    print("🌐 التطبيق سيعمل على: http://127.0.0.1:5000")
    print("🎊 المشروع جاهز للاستخدام التجاري!")
    print("=" * 64)
    print()

def main():
    """تشغيل التطبيق"""
    show_welcome_message()

    # التأكد من وجود الملفات المطلوبة
    required_files = ['app.py', 'database.py', 'templates/base.html', 'templates/login.html']
    missing_files = []

    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"❌ ملفات مفقودة: {', '.join(missing_files)}")
        print("💡 تأكد من وجود جميع ملفات المشروع")
        return

    print("📦 فحص الملفات...")
    print("✅ جميع الملفات المطلوبة موجودة")
    print()

    # تشغيل التطبيق
    try:
        print("🚀 بدء تشغيل التطبيق...")
        print("⏳ انتظر قليلاً...")
        print()

        # استيراد وتشغيل التطبيق الكامل
        from app import app

        print("✅ تم تحميل التطبيق بنجاح!")
        print("🌐 افتح المتصفح واذهب إلى: http://127.0.0.1:5000")
        print("🔄 للإيقاف: اضغط Ctrl+C")
        print()
        print("=" * 64)

        # تشغيل الخادم
        app.run(debug=True, host='127.0.0.1', port=5000)

    except ImportError as e:
        print(f"❌ خطأ في استيراد التطبيق: {e}")
        print("💡 تأكد من تثبيت جميع المكتبات المطلوبة")
        print("📋 لتثبيت المكتبات: pip install -r requirements.txt")

    except Exception as e:
        print(f"❌ خطأ في تشغيل التطبيق: {e}")
        print("💡 تحقق من إعدادات التطبيق")

if __name__ == '__main__':
    main()
