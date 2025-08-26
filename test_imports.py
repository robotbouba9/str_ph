#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار الاستيرادات والتطبيق
"""

def test_imports():
    """اختبار جميع الاستيرادات"""
    try:
        print("🔍 اختبار الاستيرادات...")
        
        # اختبار الاستيرادات الأساسية
        from app import app
        print("✅ تم استيراد app")
        
        from database import db, Product, User, Notification, ActivityLog, AuditLog
        print("✅ تم استيراد نماذج قاعدة البيانات")
        
        from forms import UserForm, ProductForm
        print("✅ تم استيراد النماذج")
        
        # اختبار إعداد التطبيق
        with app.app_context():
            print("✅ سياق التطبيق يعمل")
        
        print("\n🎉 جميع الاستيرادات تعمل بشكل صحيح!")
        return True
        
    except ImportError as e:
        print(f"❌ خطأ في الاستيراد: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ عام: {e}")
        return False

def test_database_models():
    """اختبار نماذج قاعدة البيانات"""
    try:
        print("\n🔍 اختبار نماذج قاعدة البيانات...")
        
        from app import app
        from database import db, User, Product, Notification, ActivityLog, AuditLog
        
        with app.app_context():
            # اختبار إنشاء النماذج
            user = User(username='test', role='admin')
            print("✅ نموذج User يعمل")
            
            product = Product(name='Test Phone', price_sell=100.0, quantity=10)
            print("✅ نموذج Product يعمل")
            
            notification = Notification(user_id=1, type='test', title='Test', message='Test message')
            print("✅ نموذج Notification يعمل")
            
            activity = ActivityLog(user_id=1, action='test', entity_type='test', entity_id=1)
            print("✅ نموذج ActivityLog يعمل")
            
            audit = AuditLog(user_id=1, table_name='test', record_id=1, action='INSERT')
            print("✅ نموذج AuditLog يعمل")
        
        print("🎉 جميع النماذج تعمل بشكل صحيح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار النماذج: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🧪 اختبار التطبيق")
    print("=" * 50)
    
    # اختبار الاستيرادات
    if not test_imports():
        return False
    
    # اختبار النماذج
    if not test_database_models():
        return False
    
    print("\n✅ جميع الاختبارات نجحت!")
    print("🚀 التطبيق جاهز للتشغيل")
    return True

if __name__ == "__main__":
    main()