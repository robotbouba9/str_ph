#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف التشغيل النهائي المحسن لبرنامج إدارة مخزون محل الهواتف
Final Enhanced Run Script for Phone Store Inventory Management System
"""

import os
import sys
import webbrowser
import time
from threading import Timer
from app import app, db
from database import Category, Product, Supplier, Customer

def check_database():
    """التحقق من قاعدة البيانات وإنشائها إذا لم تكن موجودة"""
    with app.app_context():
        try:
            # إنشاء الجداول إذا لم تكن موجودة
            db.create_all()
            
            # التحقق من وجود البيانات الأساسية
            if Category.query.count() == 0:
                print("📦 إضافة البيانات الأساسية...")
                
                # إضافة الفئات الأساسية
                categories = [
                    Category(name='هواتف ذكية', description='الهواتف المحمولة الذكية بجميع أنواعها وماركاتها'),
                    Category(name='سماعات', description='سماعات الرأس والأذن السلكية واللاسلكية'),
                    Category(name='كابلات الشحن', description='كابلات الشحن والبيانات بجميع الأنواع'),
                    Category(name='شواحن', description='شواحن الهواتف والأجهزة الإلكترونية'),
                    Category(name='حافظات وجرابات', description='حافظات وجرابات الهواتف الواقية'),
                    Category(name='اكسسوارات', description='اكسسوارات الهواتف المتنوعة'),
                    Category(name='بطاريات خارجية', description='بطاريات الشحن المحمولة بسعات مختلفة'),
                    Category(name='شاشات حماية', description='شاشات الحماية الزجاجية والبلاستيكية')
                ]
                
                for category in categories:
                    db.session.add(category)
                
                db.session.commit()
                print(f"✅ تم إضافة {len(categories)} فئات أساسية")
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في قاعدة البيانات: {e}")
            return False

def open_browser():
    """فتح المتصفح تلقائياً"""
    try:
        webbrowser.open('http://127.0.0.1:5000')
    except:
        pass

def print_banner():
    """طباعة شعار البرنامج"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    📱 برنامج إدارة مخزون محل الهواتف المحسن 📱              ║
║                                                              ║
║    🌟 المميزات الجديدة:                                      ║
║    ✅ نظام الفئات المتقدم                                    ║
║    ✅ البحث التلقائي الذكي                                   ║
║    ✅ وصف مفصل للمنتجات                                     ║
║    ✅ الأرقام بالتنسيق الإنجليزي                            ║
║    ✅ تصميم محسن ومتناسق                                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def main():
    """الدالة الرئيسية لتشغيل البرنامج"""
    print_banner()
    
    print("🔧 التحقق من قاعدة البيانات...")
    if not check_database():
        print("❌ فشل في إعداد قاعدة البيانات!")
        input("اضغط Enter للخروج...")
        return
    
    print("✅ قاعدة البيانات جاهزة!")
    print("\n🌐 البرنامج متاح على:")
    print("   • http://127.0.0.1:5000")
    print("   • http://localhost:5000")
    
    print("\n🚀 بدء تشغيل الخادم...")
    print("🔧 للإيقاف: اضغط Ctrl+C")
    print("=" * 60)
    
    # فتح المتصفح بعد 3 ثوانٍ
    Timer(3.0, open_browser).start()
    
    try:
        # تشغيل التطبيق
        app.run(
            debug=True,
            host='127.0.0.1',
            port=5000,
            use_reloader=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 تم إيقاف البرنامج بنجاح!")
        print("شكراً لاستخدام برنامج إدارة مخزون محل الهواتف المحسن!")
    except Exception as e:
        print(f"\n❌ خطأ في تشغيل البرنامج: {e}")
        input("اضغط Enter للخروج...")

if __name__ == '__main__':
    main()