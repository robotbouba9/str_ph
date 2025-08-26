# -*- coding: utf-8 -*-
"""
ملف تشغيل برنامج إدارة مخزون محل الهواتف
"""

import os
import sys
from app import app
from database import db, init_database

if __name__ == '__main__':
    # إنشاء المجلدات المطلوبة
    os.makedirs('instance', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)



    print("🚀 بدء تشغيل برنامج إدارة مخزون محل الهواتف")
    print("📱 يمكنك الوصول للبرنامج عبر: http://127.0.0.1:5000")
    print("👤 بيانات الدخول الافتراضية:")
    print("   اسم المستخدم: admin")
    print("   كلمة المرور: Admin@123")
    print("=" * 50)

    try:
        # تشغيل التطبيق
        app.run(
            host=app.config.get('HOST', '127.0.0.1'),
            port=app.config.get('PORT', 5000),
            debug=app.config.get('DEBUG', True),
            use_reloader=app.config.get('USE_RELOADER', True)
        )
    except KeyboardInterrupt:
        print("\n✅ تم إيقاف البرنامج بنجاح")
    except Exception as e:
        print(f"❌ خطأ في تشغيل البرنامج: {e}")
        sys.exit(1)