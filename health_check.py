#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
فحص صحة التطبيق قبل النشر
"""

import sys
import os
import importlib.util

def check_imports():
    """فحص الاستيرادات المطلوبة"""
    required_modules = [
        'flask',
        'flask_sqlalchemy',
        'werkzeug',
        'jinja2',
        'flask_wtf',
        'flask_login',
        'python_telegram_bot',
        'python_dotenv',
        'reportlab',
        'openpyxl',
        'PIL',
        'gunicorn',
        'psycopg2'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'python_telegram_bot':
                import telegram
            elif module == 'python_dotenv':
                import dotenv
            elif module == 'PIL':
                import PIL
            else:
                __import__(module)
            print(f"✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module}")
    
    return missing_modules

def check_files():
    """فحص الملفات المطلوبة"""
    required_files = [
        'app.py',
        'config.py',
        'database.py',
        'forms.py',
        'excel_export.py',
        'thermal_invoice.py',
        'requirements.txt',
        'Procfile',
        'render.yaml',
        'runtime.txt'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            missing_files.append(file)
            print(f"❌ {file}")
    
    return missing_files

def check_app_structure():
    """فحص بنية التطبيق"""
    try:
        from app import app
        print("✅ تم تحميل التطبيق بنجاح")
        
        # فحص الـ routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(rule.rule)
        
        print(f"✅ تم العثور على {len(routes)} route")
        
        return True
    except Exception as e:
        print(f"❌ خطأ في تحميل التطبيق: {e}")
        return False

def main():
    """الدالة الرئيسية للفحص"""
    print("🔍 فحص صحة التطبيق...")
    print("=" * 50)
    
    # فحص الاستيرادات
    print("\n📦 فحص المكتبات المطلوبة:")
    missing_modules = check_imports()
    
    # فحص الملفات
    print("\n📁 فحص الملفات المطلوبة:")
    missing_files = check_files()
    
    # فحص بنية التطبيق
    print("\n🏗️ فحص بنية التطبيق:")
    app_ok = check_app_structure()
    
    # النتيجة النهائية
    print("\n" + "=" * 50)
    if not missing_modules and not missing_files and app_ok:
        print("🎉 التطبيق جاهز للنشر!")
        return True
    else:
        print("⚠️ يوجد مشاكل تحتاج إلى إصلاح:")
        if missing_modules:
            print(f"   - مكتبات مفقودة: {', '.join(missing_modules)}")
        if missing_files:
            print(f"   - ملفات مفقودة: {', '.join(missing_files)}")
        if not app_ok:
            print("   - مشكلة في بنية التطبيق")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)