#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل بوت التليجرام لمتجر الهواتف
"""

import os
import sys
from telegram_bot import main

if __name__ == '__main__':
    print("🚀 بدء تشغيل بوت التليجرام...")
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {str(e)}")
        sys.exit(1)