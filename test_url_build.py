#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بناء الروابط في سياق الطلب
"""

def test_url_building():
    """اختبار بناء الروابط"""
    try:
        print("🔍 اختبار بناء الروابط...")
        
        from app import app
        
        with app.test_client() as client:
            with app.test_request_context():
                from flask import url_for
                
                # الروابط المستخدمة في base.html
                urls_to_test = [
                    'index',
                    'notifications_page', 
                    'settings_page',
                    'logout',
                    'products',
                    'advanced_search_page',
                    'categories',
                    'customers',
                    'suppliers',
                    'sales',
                    'returns',
                    'purchases',
                    'new_purchase',
                    'reports',
                    'advanced_reports',
                    'activity_logs',
                    'audit_logs',
                    'users_list'
                ]
                
                print("اختبار بناء الروابط:")
                errors = []
                
                for route in urls_to_test:
                    try:
                        url = url_for(route)
                        print(f"✅ {route}: {url}")
                    except Exception as e:
                        print(f"❌ {route}: {e}")
                        errors.append(f"{route}: {e}")
                
                if errors:
                    print(f"\n❌ وجدت {len(errors)} أخطاء:")
                    for error in errors:
                        print(f"  - {error}")
                    return False
                else:
                    print("\n🎉 جميع الروابط تعمل بشكل صحيح!")
                    return True
            
    except Exception as e:
        print(f"❌ خطأ في اختبار الروابط: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🧪 اختبار بناء روابط التطبيق")
    print("=" * 50)
    
    if test_url_building():
        print("\n✅ جميع الروابط صحيحة!")
    else:
        print("\n❌ هناك مشاكل في بعض الروابط!")

if __name__ == "__main__":
    main()