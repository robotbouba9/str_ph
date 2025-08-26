# -*- coding: utf-8 -*-
"""
"""

import os
import sys
from app import app
from database import db, init_database

if __name__ == '__main__':
    # إنشاء المجلدات المطلوبة
    os.makedirs('instance', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)










    try:
        # تشغيل التطبيق
        app.run(
            host=app.config.get('HOST', '127.0.0.1'),
            port=app.config.get('PORT', 5000),
            debug=app.config.get('DEBUG', True),
            use_reloader=app.config.get('USE_RELOADER', True)
        )
    except KeyboardInterrupt:
        pass
    except Exception as e:
        sys.exit(1)