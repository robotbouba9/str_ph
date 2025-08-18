#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعداد بوت التليجرام - إنشاء ملف .env مع رمز البوت
"""

import os

def setup_telegram_bot():
    print("🤖 إعداد بوت التليجرام")
    print("=" * 50)
    print()
    
    # Check if .env file already exists
    if os.path.exists('.env'):
        print("⚠️  ملف .env موجود بالفعل")
        overwrite = input("هل تريد استبداله؟ (y/n): ").lower()
        if overwrite != 'y':
            print("تم إلغاء العملية")
            return
    
    print("للحصول على رمز البوت:")
    print("1. افتح تليجرام وابحث عن @BotFather")
    print("2. أرسل /newbot")
    print("3. اتبع التعليمات لإنشاء بوت جديد")
    print("4. انسخ الرمز الذي سيرسله لك")
    print()
    
    token = input("أدخل رمز البوت (Bot Token): ").strip()
    
    if not token:
        print("❌ لم تدخل رمز البوت!")
        return
    
    # Validate token format (basic check)
    if ':' not in token or len(token) < 40:
        print("❌ رمز البوت غير صحيح!")
        print("تأكد من أن الرمز يحتوي على : ويبدأ برقم")
        return
    
    # Create .env file
    env_content = f"""# متغيرات البيئة لمتجر الهواتف
TELEGRAM_BOT_TOKEN={token}
DATABASE_URL=sqlite:///instance/phone_store.db
SECRET_KEY=your_secret_key_here_change_this
DEBUG=True
PORT=5000
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ تم إنشاء ملف .env بنجاح!")
        print("🚀 يمكنك الآن تشغيل البوت باستخدام: python run_bot.py")
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء ملف .env: {str(e)}")

if __name__ == '__main__':
    setup_telegram_bot()