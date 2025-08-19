#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل مباشر لتطبيق متجر الهواتف
"""

import os
import sys

# إضافة المسار الحالي إلى sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    """تشغيل التطبيق مباشرة من app.py"""
    try:
        print("🚀 بدء تشغيل تطبيق متجر الهواتف...")
        print("⏳ جاري تحميل التطبيق...")

        # استيراد وتشغيل التطبيق
        from app_corrected import app

        print("✅ تم تحميل التطبيق بنجاح!")
        print("🌐 افتح المتصفح واذهب إلى: http://127.0.0.1:5000")
        print("🔄 للإيقاف: اضغط Ctrl+C")
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
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
