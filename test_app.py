#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بسيط للتطبيق
"""

import os
import sys

# إضافة المجلد الحالي إلى المسار
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    print("✅ تم تحميل التطبيق بنجاح")
    
    with app.app_context():
        from database import db
        print("✅ تم الاتصال بقاعدة البيانات")
        
        # إنشاء الجداول
        db.create_all()
        print("✅ تم إنشاء الجداول")
        
        # فحص الـ routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(rule.rule)
        
        print(f"✅ تم العثور على {len(routes)} route")
        print("🎉 التطبيق جاهز للعمل!")
        
except Exception as e:
    print(f"❌ خطأ: {e}")
    import traceback
    traceback.print_exc()