# -*- coding: utf-8 -*-
"""
أداة فحص النظام والتحقق من سلامة برنامج إدارة مخزون محل الهواتف
"""

import os
import sys
import importlib
import subprocess
from datetime import datetime

def check_python_version():
    """التحقق من إصدار Python"""
    print("🐍 فحص إصدار Python...")
    version = sys.version_info
    
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - مدعوم")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - غير مدعوم")
        print("يرجى تثبيت Python 3.7 أو أحدث")
        return False

def check_required_modules():
    """التحقق من المكتبات المطلوبة"""
    print("\n📦 فحص المكتبات المطلوبة...")
    
    required_modules = {
        'flask': 'Flask==2.3.3',
        'flask_sqlalchemy': 'Flask-SQLAlchemy==3.0.5',
        'werkzeug': 'Werkzeug==2.3.7',
        'jinja2': 'Jinja2==3.1.2',
        'tkinter': 'tkinter (مدمج مع Python)'
    }
    
    missing_modules = []
    
    for module, description in required_modules.items():
        try:
            if module == 'tkinter':
                import tkinter
            else:
                importlib.import_module(module)
            print(f"✅ {description}")
        except ImportError:
            print(f"❌ {description} - غير مثبت")
            missing_modules.append(module)
    
    return len(missing_modules) == 0, missing_modules

def check_required_files():
    """التحقق من الملفات المطلوبة"""
    print("\n📁 فحص الملفات المطلوبة...")
    
    required_files = [
        'app.py',
        'database.py',
        'desktop_app.py',
        'run.py',
        'requirements.txt',
        'config.py',
        'templates/base.html',
        'templates/index.html',
        'templates/products.html',
        'templates/customers.html',
        'templates/suppliers.html',
        'templates/sales.html'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - مفقود")
            missing_files.append(file_path)
    
    return len(missing_files) == 0, missing_files

def check_database():
    """التحقق من قاعدة البيانات"""
    print("\n🗄️ فحص قاعدة البيانات...")
    
    try:
        if os.path.exists('phone_store.db'):
            file_size = os.path.getsize('phone_store.db')
            print(f"✅ قاعدة البيانات موجودة ({file_size} بايت)")
            
            # محاولة الاتصال بقاعدة البيانات
            from database import db, Product, Customer, Supplier, Sale
            from app import app
            
            with app.app_context():
                products_count = Product.query.count()
                customers_count = Customer.query.count()
                suppliers_count = Supplier.query.count()
                sales_count = Sale.query.count()
                
                print(f"📊 المنتجات: {products_count}")
                print(f"👥 العملاء: {customers_count}")
                print(f"🚚 الموردين: {suppliers_count}")
                print(f"🧾 المبيعات: {sales_count}")
                
            return True
        else:
            print("⚠️ قاعدة البيانات غير موجودة - سيتم إنشاؤها عند التشغيل الأول")
            return True
            
    except Exception as e:
        print(f"❌ خطأ في قاعدة البيانات: {e}")
        return False

def check_ports():
    """التحقق من توفر المنافذ"""
    print("\n🌐 فحص المنافذ...")
    
    import socket
    
    ports_to_check = [5000, 5001, 5002]
    available_ports = []
    
    for port in ports_to_check:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            print(f"✅ المنفذ {port} متاح")
            available_ports.append(port)
        except OSError:
            print(f"⚠️ المنفذ {port} مستخدم")
    
    return len(available_ports) > 0, available_ports

def check_permissions():
    """التحقق من الصلاحيات"""
    print("\n🔐 فحص الصلاحيات...")
    
    try:
        # التحقق من صلاحية الكتابة
        test_file = 'test_permissions.tmp'
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("✅ صلاحية الكتابة متوفرة")
        
        # التحقق من صلاحية إنشاء المجلدات
        test_dir = 'test_dir'
        os.makedirs(test_dir, exist_ok=True)
        os.rmdir(test_dir)
        print("✅ صلاحية إنشاء المجلدات متوفرة")
        
        return True
        
    except Exception as e:
        print(f"❌ مشكلة في الصلاحيات: {e}")
        return False

def install_missing_modules(missing_modules):
    """تثبيت المكتبات المفقودة"""
    if not missing_modules:
        return True
    
    print(f"\n📥 تثبيت المكتبات المفقودة...")
    
    try:
        # تثبيت من requirements.txt
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt', '--user'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ تم تثبيت المكتبات بنجاح")
            return True
        else:
            print(f"❌ فشل في تثبيت المكتبات: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في تثبيت المكتبات: {e}")
        return False

def run_quick_test():
    """تشغيل اختبار سريع"""
    print("\n🧪 تشغيل اختبار سريع...")
    
    try:
        # اختبار استيراد الوحدات الأساسية
        from app import app
        from database import db, Product, Customer, Supplier, Sale
        from desktop_app import PhoneStoreApp
        
        print("✅ جميع الوحدات تعمل بشكل صحيح")
        
        # اختبار إنشاء التطبيق
        with app.app_context():
            db.create_all()
        
        print("✅ قاعدة البيانات تعمل بشكل صحيح")
        return True
        
    except Exception as e:
        print(f"❌ فشل الاختبار السريع: {e}")
        return False

def generate_report():
    """إنشاء تقرير الفحص"""
    print("\n📋 إنشاء تقرير الفحص...")
    
    report = f"""
تقرير فحص النظام - برنامج إدارة مخزون محل الهواتف
{'='*60}
تاريخ الفحص: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
نظام التشغيل: {os.name}
إصدار Python: {sys.version}
مجلد العمل: {os.getcwd()}

النتائج:
- إصدار Python: {'✅' if check_python_version() else '❌'}
- المكتبات المطلوبة: {'✅' if check_required_modules()[0] else '❌'}
- الملفات المطلوبة: {'✅' if check_required_files()[0] else '❌'}
- قاعدة البيانات: {'✅' if check_database() else '❌'}
- المنافذ المتاحة: {'✅' if check_ports()[0] else '❌'}
- الصلاحيات: {'✅' if check_permissions() else '❌'}

التوصيات:
- استخدم start_desktop.bat للتشغيل السريع
- راجع README.md للتوثيق الكامل
- استخدم manage_db.py لإدارة قاعدة البيانات
"""
    
    try:
        with open('system_check_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        print("✅ تم حفظ التقرير في: system_check_report.txt")
    except Exception as e:
        print(f"⚠️ لم يتم حفظ التقرير: {e}")
    
    return report

def main():
    """الدالة الرئيسية"""
    print("🔍 أداة فحص النظام")
    print("برنامج إدارة مخزون محل الهواتف")
    print("=" * 50)
    
    all_checks_passed = True
    
    # فحص إصدار Python
    if not check_python_version():
        all_checks_passed = False
    
    # فحص المكتبات
    modules_ok, missing_modules = check_required_modules()
    if not modules_ok:
        all_checks_passed = False
        
        # محاولة تثبيت المكتبات المفقودة
        install_choice = input("\nهل تريد محاولة تثبيت المكتبات المفقودة؟ (y/N): ")
        if install_choice.lower() == 'y':
            if install_missing_modules(missing_modules):
                modules_ok, _ = check_required_modules()
                if modules_ok:
                    all_checks_passed = True
    
    # فحص الملفات
    if not check_required_files()[0]:
        all_checks_passed = False
    
    # فحص قاعدة البيانات
    if not check_database():
        all_checks_passed = False
    
    # فحص المنافذ
    ports_ok, available_ports = check_ports()
    if not ports_ok:
        print("⚠️ تحذير: لا توجد منافذ متاحة")
    
    # فحص الصلاحيات
    if not check_permissions():
        all_checks_passed = False
    
    # اختبار سريع
    if all_checks_passed:
        if not run_quick_test():
            all_checks_passed = False
    
    # النتيجة النهائية
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 جميع الفحوصات نجحت! البرنامج جاهز للتشغيل")
        print("\nللتشغيل:")
        print("- انقر نقراً مزدوجاً على start_desktop.bat")
        print("- أو انقر على start_web.bat")
    else:
        print("⚠️ بعض الفحوصات فشلت. يرجى مراجعة الأخطاء أعلاه")
        print("\nللمساعدة:")
        print("- راجع README.md")
        print("- راجع QUICK_START.md")
    
    # إنشاء التقرير
    generate_report()
    
    input("\nاضغط Enter للخروج...")

if __name__ == "__main__":
    main()