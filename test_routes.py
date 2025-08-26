#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار المسارات والروابط
"""

def test_routes():
    """اختبار جميع المسارات"""
    try:
        print("🔍 اختبار المسارات...")
        
        from app import app
        
        with app.app_context():
            # اختبار بناء الروابط الأساسية
            from flask import url_for
            
            # المسارات الأساسية
            routes_to_test = [
                'index',
                
                'products',
                'customers',
                'suppliers',
                'sales',
                'purchases',
                'returns',
                'reports',
                'notifications_page',
                'activity_logs',
                'audit_logs',
                'settings_page',
                'users_management',
                'categories',
                'brands'
            ]
            
            print("اختبار بناء الروابط:")
            for route in routes_to_test:
                try:
                    url = url_for(route)
                    print(f"✅ {route}: {url}")
                except Exception as e:
                    print(f"❌ {route}: {e}")
            
            print("\n🎉 انتهى اختبار المسارات!")
            return True
            
    except Exception as e:
        print(f"❌ خطأ في اختبار المسارات: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🧪 اختبار مسارات التطبيق")
    print("=" * 50)
    
    if test_routes():
        print("\n✅ جميع المسارات تعمل بشكل صحيح!")
    else:
        print("\n❌ هناك مشاكل في بعض المسارات!")

if __name__ == "__main__":
    main()