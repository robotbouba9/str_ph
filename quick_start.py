#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل سريع للتطبيق مع إعداد أولي
"""

import os
import sys
from pathlib import Path

def create_directories():
    """إنشاء المجلدات المطلوبة"""
    directories = ['instance', 'uploads', 'cache', 'backups', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def setup_env():
    """إعداد متغيرات البيئة الأساسية"""
    if not Path('.env').exists():
        env_content = """# إعدادات التطبيق
APP_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///instance/phone_store.db

# إعدادات الخادم
HOST=0.0.0.0
PORT=5000

# إعدادات التطبيق
DEBUG=true
"""
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ تم إنشاء ملف .env")

def main():
    """الدالة الرئيسية"""
    print("🚀 تشغيل سريع لبرنامج إدارة مخزون الهواتف")
    print("=" * 50)
    
    # إنشاء المجلدات
    create_directories()
    print("✅ تم إنشاء المجلدات المطلوبة")
    
    # إعداد البيئة
    setup_env()
    
    # تشغيل التطبيق
    try:
        from app import app
        print("\n🌐 التطبيق يعمل على: http://localhost:5000")
        print("👤 المستخدم الافتراضي: owner")
        print("🔑 كلمة المرور الافتراضية: Owner@123")
        print("💡 زر /init_database لإنشاء قاعدة البيانات")
        print("=" * 50)
        
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل التطبيق: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if '--auto-commits' in sys.argv:
        print("✅ Auto-commits activés")
        # Ajouter le code pour les auto-commits ici
    main()
