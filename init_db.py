#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إنشاء قاعدة البيانات والجداول
"""

import os
import sys

# إضافة المجلد الحالي إلى المسار
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_database():
    """إنشاء قاعدة البيانات والجداول"""
    try:
        from app import app
        from database import create_tables
        
        print("🔧 إنشاء قاعدة البيانات...")
        
        # إنشاء الجداول والبيانات الافتراضية
        create_tables(app)
        
        print("✅ تم إنشاء قاعدة البيانات بنجاح!")
        print("🎉 التطبيق جاهز للاستخدام!")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء قاعدة البيانات: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)