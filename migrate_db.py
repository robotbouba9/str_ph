#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة ترحيل وتحديث قاعدة البيانات
"""

import os
import sys
from datetime import datetime
from pathlib import Path

def backup_database():
    """إنشاء نسخة احتياطية من قاعدة البيانات"""
    db_path = Path("instance/phone_store.db")
    if not db_path.exists():
        print("⚠️  قاعدة البيانات غير موجودة")
        return None
    
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"phone_store_backup_{timestamp}.db"
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ تم إنشاء نسخة احتياطية: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ فشل في إنشاء النسخة الاحتياطية: {e}")
        return None

def update_database_schema():
    """تحديث مخطط قاعدة البيانات"""
    try:
        from app import app, db
        from database import (Product, Customer, Supplier, Sale, SaleItem, 
                            Category, PurchaseInvoice, PurchaseItem, 
                            StoreSettings, Brand, Return, ReturnItem, 
                            User, Notification, ActivityLog, AuditLog)
        
        with app.app_context():
            print("🔄 تحديث مخطط قاعدة البيانات...")
            
            # إنشاء الجداول الجديدة إذا لم تكن موجودة
            db.create_all()
            
            # التحقق من وجود الجداول الجديدة
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            required_tables = [
                'notifications', 'activity_logs', 'audit_logs'
            ]
            
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            if missing_tables:
                print(f"📝 إنشاء الجداول المفقودة: {', '.join(missing_tables)}")
                db.create_all()
            
            print("✅ تم تحديث مخطط قاعدة البيانات")
            return True
            
    except Exception as e:
        print(f"❌ فشل في تحديث قاعدة البيانات: {e}")
        return False

def add_missing_columns():
    """إضافة الأعمدة المفقودة"""
    try:
        from app import app, db
        
        with app.app_context():
            print("🔄 فحص الأعمدة المفقودة...")
            
            # قائمة التحديثات المطلوبة
            updates = []
            
            # فحص جدول المستخدمين
            try:
                result = db.engine.execute("PRAGMA table_info(users)")
                columns = [row[1] for row in result]
                
                if 'is_active' not in columns:
                    updates.append("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
                
                
                    
            except Exception as e:
                print(f"⚠️  تحذير في فحص جدول المستخدمين: {e}")
            
            # تنفيذ التحديثات
            for update in updates:
                try:
                    db.engine.execute(update)
                    print(f"✅ تم تنفيذ: {update}")
                except Exception as e:
                    print(f"⚠️  فشل في تنفيذ: {update} - {e}")
            
            if updates:
                db.session.commit()
                print("✅ تم تحديث الأعمدة")
            else:
                print("✅ جميع الأعمدة موجودة")
            
            return True
            
    except Exception as e:
        print(f"❌ فشل في إضافة الأعمدة: {e}")
        return False

def verify_data_integrity():
    """التحقق من سلامة البيانات"""
    try:
        from app import app, db
        from database import User, Product, Category, Brand
        
        with app.app_context():
            print("🔍 فحص سلامة البيانات...")
            
            # فحص المستخدم الافتراضي
            owner = User.query.filter_by(username='owner').first()
            if not owner:
                print("⚠️  المستخدم الافتراضي غير موجود")
                return False
            
            # فحص الفئات الأساسية
            categories_count = Category.query.count()
            if categories_count == 0:
                print("⚠️  لا توجد فئات في قاعدة البيانات")
            
            # فحص الماركات الأساسية
            brands_count = Brand.query.count()
            if brands_count == 0:
                print("⚠️  لا توجد ماركات في قاعدة البيانات")
            
            print("✅ تم فحص سلامة البيانات")
            return True
            
    except Exception as e:
        print(f"❌ فشل في فحص سلامة البيانات: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🔧 أداة ترحيل وتحديث قاعدة البيانات")
    print("=" * 50)
    
    # إنشاء نسخة احتياطية
    backup_path = backup_database()
    if not backup_path:
        response = input("هل تريد المتابعة بدون نسخة احتياطية؟ (y/N): ")
        if response.lower() not in ['y', 'yes', 'نعم']:
            print("تم إلغاء العملية")
            sys.exit(1)
    
    # تحديث مخطط قاعدة البيانات
    if not update_database_schema():
        print("❌ فشل في تحديث مخطط قاعدة البيانات")
        sys.exit(1)
    
    # إضافة الأعمدة المفقودة
    if not add_missing_columns():
        print("❌ فشل في إضافة الأعمدة المفقودة")
        sys.exit(1)
    
    # التحقق من سلامة البيانات
    if not verify_data_integrity():
        print("⚠️  تحذير: مشاكل في سلامة البيانات")
    
    print("\n✅ تم تحديث قاعدة البيانات بنجاح!")
    print("=" * 50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 تم إلغاء العملية")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        sys.exit(1)