#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تثبيت المتطلبات الجديدة للمميزات المتقدمة
"""

import subprocess
import sys
import os

def install_requirements():
    """تثبيت المتطلبات"""
    print("🔧 تثبيت المتطلبات الجديدة...")
    print("=" * 50)
    
    try:
        # تثبيت المتطلبات
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ تم تثبيت جميع المتطلبات بنجاح!")
            print("\n📦 المكتبات المثبتة:")
            print("- reportlab: لإنشاء الفواتير الحرارية PDF")
            print("- openpyxl: لتصدير Excel")
            print("- weasyprint: لتحويل HTML إلى PDF")
            print("- Pillow: لمعالجة الصور")
            
            print("\n🎉 المشروع جاهز الآن مع جميع المميزات الجديدة:")
            print("✅ فواتير حرارية احترافية (80mm)")
            print("✅ تصدير Excel للتقارير")
            print("✅ العملة الجزائرية (د.ج)")
            print("✅ فواتير الموردين مع تحديث المخزون التلقائي")
            print("✅ تقارير متقدمة مع فلاتر التاريخ")
            
            print("\n🚀 لتشغيل التطبيق:")
            print("python run_web.py")
            
        else:
            print("❌ خطأ في تثبيت المتطلبات:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")

if __name__ == '__main__':
    install_requirements()