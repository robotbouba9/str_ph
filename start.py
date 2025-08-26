#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف تشغيل محسن لبرنامج إدارة مخزون محل الهواتف
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """التحقق من إصدار Python"""
    if sys.version_info < (3, 8):
        print("❌ يتطلب Python 3.8 أو أحدث")
        print(f"الإصدار الحالي: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

def check_virtual_env():
    """التحقق من البيئة الافتراضية"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ البيئة الافتراضية مفعلة")
        return True
    else:
        print("⚠️  لم يتم تفعيل البيئة الافتراضية")
        return False

def install_requirements():
    """تثبيت المتطلبات"""
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        print("📦 تثبيت المتطلبات...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ تم تثبيت المتطلبات بنجاح")
        except subprocess.CalledProcessError:
            print("❌ فشل في تثبيت المتطلبات")
            return False
    else:
        print("❌ ملف requirements.txt غير موجود")
        return False
    return True

def setup_environment():
    """إعداد متغيرات البيئة"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📝 إنشاء ملف .env من المثال...")
        try:
            import shutil
            shutil.copy(env_example, env_file)
            print("✅ تم إنشاء ملف .env")
            print("⚠️  يرجى تعديل الإعدادات في ملف .env حسب الحاجة")
        except Exception as e:
            print(f"❌ فشل في إنشاء ملف .env: {e}")
            return False
    elif env_file.exists():
        print("✅ ملف .env موجود")
    else:
        print("⚠️  ملف .env غير موجود")
    
    return True

def create_directories():
    """إنشاء المجلدات المطلوبة"""
    directories = ['instance', 'uploads', 'cache', 'backups', 'logs']
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ تم إنشاء مجلد: {directory}")
            except Exception as e:
                print(f"❌ فشل في إنشاء مجلد {directory}: {e}")
                return False
        else:
            print(f"✅ مجلد موجود: {directory}")
    
    return True

def check_database():
    """التحقق من قاعدة البيانات"""
    db_file = Path("instance/phone_store.db")
    if db_file.exists():
        print("✅ قاعدة البيانات موجودة")
        return True
    else:
        print("⚠️  قاعدة البيانات غير موجودة - سيتم إنشاؤها عند التشغيل")
        print("💡 زر /init_database بعد تشغيل التطبيق لإنشاء قاعدة البيانات")
        return True

def start_application():
    """تشغيل التطبيق"""
    print("\n🚀 تشغيل التطبيق...")
    print("=" * 50)
    print("📱 برنامج إدارة مخزون محل الهواتف")
    print("🌐 الرابط: http://localhost:5000")
    print("👤 المستخدم الافتراضي: owner")
    print("🔑 كلمة المرور الافتراضية: Owner@123")
    print("=" * 50)
    
    try:
        # تشغيل التطبيق
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=True)
    except ImportError as e:
        print(f"❌ خطأ في استيراد التطبيق: {e}")
        print("💡 تأكد من تثبيت جميع المتطلبات")
        return False
    except Exception as e:
        print(f"❌ خطأ في تشغيل التطبيق: {e}")
        return False
    
    return True

def main():
    """الدالة الرئيسية"""
    print("🔧 فحص النظام وإعداد التطبيق...")
    print("=" * 50)
    
    # فحص إصدار Python
    check_python_version()
    
    # فحص البيئة الافتراضية
    venv_active = check_virtual_env()
    if not venv_active:
        response = input("هل تريد المتابعة بدون بيئة افتراضية؟ (y/N): ")
        if response.lower() not in ['y', 'yes', 'نعم']:
            print("💡 قم بتفعيل البيئة الافتراضية أولاً:")
            print("   python -m venv venv")
            print("   venv\\Scripts\\activate  # Windows")
            print("   source venv/bin/activate  # Linux/Mac")
            sys.exit(1)
    
    # تثبيت المتطلبات
    if not install_requirements():
        sys.exit(1)
    
    # إعداد البيئة
    if not setup_environment():
        sys.exit(1)
    
    # إنشاء المجلدات
    if not create_directories():
        sys.exit(1)
    
    # فحص قاعدة البيانات
    check_database()
    
    print("\n✅ تم إعداد النظام بنجاح!")
    print("=" * 50)
    
    # تشغيل التطبيق
    start_application()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 تم إيقاف التطبيق بواسطة المستخدم")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        sys.exit(1)