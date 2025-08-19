#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل تطبيق الويب لمتجر الهواتف - نسخة مصححة
"""

from app import app

if __name__ == '__main__':
    print("🚀 بدء تشغيل تطبيق الويب (النسخة المصححة)...")
    print("🌐 يمكنك الوصول للتطبيق على: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)