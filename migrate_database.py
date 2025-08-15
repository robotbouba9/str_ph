#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف ترحيل قاعدة البيانات لإضافة الحقول الجديدة
Database Migration Script for Adding New Fields
"""

import sqlite3
import os
from app import app

def migrate_database():
    """ترحيل قاعدة البيانات لإضافة الحقول الجديدة"""
    
    db_path = os.path.join('instance', 'phone_store.db')
    
    if not os.path.exists(db_path):
        print("❌ قاعدة البيانات غير موجودة!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 بدء ترحيل قاعدة البيانات...")
        
        # التحقق من وجود العمود description
        cursor.execute("PRAGMA table_info(products)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'description' not in columns:
            print("📝 إضافة عمود الوصف...")
            cursor.execute("ALTER TABLE products ADD COLUMN description TEXT")
            
        if 'category_id' not in columns:
            print("🏷️ إضافة عمود الفئة...")
            cursor.execute("ALTER TABLE products ADD COLUMN category_id INTEGER")
            
        # التحقق من وجود جدول الفئات
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categories'")
        if not cursor.fetchone():
            print("🏷️ إنشاء جدول الفئات...")
            cursor.execute('''
                CREATE TABLE categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # إضافة فئات افتراضية
            default_categories = [
                ('هواتف ذكية', 'الهواتف المحمولة الذكية بجميع أنواعها وماركاتها'),
                ('سماعات', 'سماعات الرأس والأذن السلكية واللاسلكية'),
                ('كابلات الشحن', 'كابلات الشحن والبيانات بجميع الأنواع'),
                ('شواحن', 'شواحن الهواتف والأجهزة الإلكترونية'),
                ('حافظات وجرابات', 'حافظات وجرابات الهواتف الواقية'),
                ('اكسسوارات', 'اكسسوارات الهواتف المتنوعة'),
                ('بطاريات خارجية', 'بطاريات الشحن المحمولة بسعات مختلفة'),
                ('شاشات حماية', 'شاشات الحماية الزجاجية والبلاستيكية')
            ]
            
            cursor.executemany(
                "INSERT INTO categories (name, description) VALUES (?, ?)",
                default_categories
            )
            
        # حذف العمود القديم storage إذا كان موجوداً
        if 'storage' in columns:
            print("🗑️ إزالة عمود التخزين القديم...")
            # في SQLite لا يمكن حذف العمود مباشرة، لكن يمكن تجاهله
            pass
            
        conn.commit()
        conn.close()
        
        print("✅ تم ترحيل قاعدة البيانات بنجاح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في ترحيل قاعدة البيانات: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🔧 أداة ترحيل قاعدة البيانات")
    print("=" * 40)
    
    if migrate_database():
        print("\n🎉 تم الترحيل بنجاح! يمكنك الآن تشغيل البرنامج.")
    else:
        print("\n❌ فشل في الترحيل. يرجى المحاولة مرة أخرى.")

if __name__ == '__main__':
    main()