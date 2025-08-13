# -*- coding: utf-8 -*-
"""
أدوات إدارة قاعدة البيانات لبرنامج إدارة مخزون محل الهواتف
"""

import os
import sys
import shutil
from datetime import datetime
from database import db, init_database, Product, Customer, Supplier, Sale, SaleItem

def create_database():
    """إنشاء قاعدة البيانات"""
    try:
        from app import app
        with app.app_context():
            db.create_all()
            print("✅ تم إنشاء قاعدة البيانات بنجاح")
            return True
    except Exception as e:
        print(f"❌ خطأ في إنشاء قاعدة البيانات: {e}")
        return False

def reset_database():
    """إعادة تعيين قاعدة البيانات"""
    try:
        if os.path.exists('phone_store.db'):
            # إنشاء نسخة احتياطية قبل الحذف
            backup_name = f"phone_store_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2('phone_store.db', backup_name)
            print(f"📁 تم إنشاء نسخة احتياطية: {backup_name}")
            
            # حذف قاعدة البيانات الحالية
            os.remove('phone_store.db')
            print("🗑️ تم حذف قاعدة البيانات القديمة")
        
        # إنشاء قاعدة بيانات جديدة
        if create_database():
            print("✅ تم إعادة تعيين قاعدة البيانات بنجاح")
            return True
        return False
    except Exception as e:
        print(f"❌ خطأ في إعادة تعيين قاعدة البيانات: {e}")
        return False

def backup_database():
    """إنشاء نسخة احتياطية من قاعدة البيانات"""
    try:
        if not os.path.exists('phone_store.db'):
            print("❌ قاعدة البيانات غير موجودة")
            return False
        
        # إنشاء مجلد النسخ الاحتياطية إذا لم يكن موجوداً
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # إنشاء اسم الملف
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = os.path.join(backup_dir, f'phone_store_backup_{timestamp}.db')
        
        # نسخ قاعدة البيانات
        shutil.copy2('phone_store.db', backup_filename)
        print(f"✅ تم إنشاء النسخة الاحتياطية: {backup_filename}")
        return backup_filename
    except Exception as e:
        print(f"❌ خطأ في إنشاء النسخة الاحتياطية: {e}")
        return False

def restore_database(backup_file):
    """استعادة قاعدة البيانات من نسخة احتياطية"""
    try:
        if not os.path.exists(backup_file):
            print(f"❌ ملف النسخة الاحتياطية غير موجود: {backup_file}")
            return False
        
        # إنشاء نسخة احتياطية من قاعدة البيانات الحالية
        if os.path.exists('phone_store.db'):
            current_backup = f"phone_store_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2('phone_store.db', current_backup)
            print(f"📁 تم حفظ قاعدة البيانات الحالية: {current_backup}")
        
        # استعادة النسخة الاحتياطية
        shutil.copy2(backup_file, 'phone_store.db')
        print(f"✅ تم استعادة قاعدة البيانات من: {backup_file}")
        return True
    except Exception as e:
        print(f"❌ خطأ في استعادة قاعدة البيانات: {e}")
        return False

def show_database_info():
    """عرض معلومات قاعدة البيانات"""
    try:
        from app import app
        with app.app_context():
            print("📊 معلومات قاعدة البيانات:")
            print("=" * 40)
            
            # عدد المنتجات
            products_count = Product.query.count()
            print(f"📱 المنتجات: {products_count}")
            
            # عدد العملاء
            customers_count = Customer.query.count()
            print(f"👥 العملاء: {customers_count}")
            
            # عدد الموردين
            suppliers_count = Supplier.query.count()
            print(f"🚚 الموردين: {suppliers_count}")
            
            # عدد المبيعات
            sales_count = Sale.query.count()
            print(f"🧾 المبيعات: {sales_count}")
            
            # إجمالي المبيعات
            total_revenue = db.session.query(db.func.sum(Sale.final_amount)).scalar() or 0
            print(f"💰 إجمالي المبيعات: {total_revenue:.2f} جنيه")
            
            # المنتجات منخفضة المخزون
            low_stock = Product.query.filter(Product.quantity <= Product.min_quantity).count()
            print(f"⚠️ منخفض المخزون: {low_stock}")
            
            print("=" * 40)
            
            # معلومات الملف
            if os.path.exists('phone_store.db'):
                file_size = os.path.getsize('phone_store.db')
                file_size_mb = file_size / (1024 * 1024)
                print(f"📁 حجم الملف: {file_size_mb:.2f} ميجابايت")
                
                file_time = datetime.fromtimestamp(os.path.getmtime('phone_store.db'))
                print(f"🕒 آخر تعديل: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
    except Exception as e:
        print(f"❌ خطأ في عرض معلومات قاعدة البيانات: {e}")

def clean_old_backups(days=30):
    """حذف النسخ الاحتياطية القديمة"""
    try:
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            print("📁 مجلد النسخ الاحتياطية غير موجود")
            return
        
        cutoff_time = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for filename in os.listdir(backup_dir):
            if filename.startswith('phone_store_backup_') and filename.endswith('.db'):
                file_path = os.path.join(backup_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_time < cutoff_time:
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"🗑️ تم حذف: {filename}")
        
        print(f"✅ تم حذف {deleted_count} نسخة احتياطية قديمة")
        
    except Exception as e:
        print(f"❌ خطأ في تنظيف النسخ الاحتياطية: {e}")

def main():
    """الدالة الرئيسية"""
    print("🔧 أدوات إدارة قاعدة البيانات")
    print("=" * 50)
    print("1. إنشاء قاعدة البيانات")
    print("2. إعادة تعيين قاعدة البيانات")
    print("3. إنشاء نسخة احتياطية")
    print("4. استعادة من نسخة احتياطية")
    print("5. عرض معلومات قاعدة البيانات")
    print("6. تنظيف النسخ الاحتياطية القديمة")
    print("7. خروج")
    print("=" * 50)
    
    while True:
        try:
            choice = input("\nاختر رقم العملية (1-7): ").strip()
            
            if choice == '1':
                create_database()
            elif choice == '2':
                confirm = input("هل أنت متأكد من إعادة تعيين قاعدة البيانات؟ (y/N): ")
                if confirm.lower() == 'y':
                    reset_database()
                else:
                    print("تم إلغاء العملية")
            elif choice == '3':
                backup_database()
            elif choice == '4':
                backup_file = input("أدخل مسار ملف النسخة الاحتياطية: ").strip()
                restore_database(backup_file)
            elif choice == '5':
                show_database_info()
            elif choice == '6':
                days = input("أدخل عدد الأيام (افتراضي 30): ").strip()
                days = int(days) if days.isdigit() else 30
                clean_old_backups(days)
            elif choice == '7':
                print("👋 وداعاً!")
                break
            else:
                print("❌ اختيار غير صحيح")
                
        except KeyboardInterrupt:
            print("\n👋 تم إنهاء البرنامج")
            break
        except Exception as e:
            print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    main()