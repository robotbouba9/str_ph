# -*- coding: utf-8 -*-
"""
ملف تشغيل برنامج إدارة مخزون محل الهواتف
"""

import sys
import os

# إضافة المجلد الحالي لمسار Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """الدالة الرئيسية لتشغيل البرنامج"""
    print("=" * 50)
    print("برنامج إدارة مخزون محل الهواتف")
    print("=" * 50)
    print()
    print("اختر طريقة التشغيل:")
    print("1. تطبيق سطح المكتب (مع واجهة ويب مدمجة)")
    print("2. خادم ويب فقط")
    print("3. إنهاء")
    print()
    
    while True:
        try:
            choice = input("اختر رقم (1-3): ").strip()
            
            if choice == "1":
                print("\nجاري تشغيل تطبيق سطح المكتب...")
                from desktop_app import main as desktop_main
                desktop_main()
                break
                
            elif choice == "2":
                print("\nجاري تشغيل خادم الويب...")
                print("يمكنك الوصول للبرنامج عبر: http://localhost:5000")
                print("اضغط Ctrl+C لإيقاف الخادم")
                from app import app
                app.run(debug=True, host='127.0.0.1', port=5000)
                break
                
            elif choice == "3":
                print("تم إنهاء البرنامج.")
                break
                
            else:
                print("اختيار غير صحيح. يرجى اختيار رقم من 1 إلى 3.")
                
        except KeyboardInterrupt:
            print("\n\nتم إنهاء البرنامج.")
            break
        except Exception as e:
            print(f"\nخطأ: {str(e)}")
            print("يرجى التأكد من تثبيت المتطلبات: pip install -r requirements.txt")
            break

if __name__ == "__main__":
    main()