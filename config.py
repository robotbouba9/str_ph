# -*- coding: utf-8 -*-
"""
ملف إعدادات برنامج إدارة مخزون محل الهواتف
"""

import os
from datetime import timedelta

class Config:
    """إعدادات البرنامج الأساسية"""
    
    # إعدادات قاعدة البيانات
    _db_url = os.environ.get('DATABASE_URL')
    if _db_url and _db_url.startswith('postgres://'):
        # توافق Render/Heroku مع SQLAlchemy
        _db_url = _db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
    SQLALCHEMY_DATABASE_URI = _db_url or f'sqlite:///{os.path.abspath("instance/phone_store.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # إعدادات الأمان
    # يجب تغيير هذا المفتاح السري في بيئة الإنتاج باستخدام متغير بيئة
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'phone-store-secret-key-2024'
    
    # إعدادات الجلسة
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # إعدادات التطبيق
    APP_NAME = "برنامج إدارة مخزون محل الهواتف"
    APP_VERSION = "1.0.0"
    
    # إعدادات الخادم
    DEFAULT_HOST = '127.0.0.1'
    DEFAULT_PORT = 5000
    DEBUG = True
    
    # إعدادات التقارير
    REPORTS_PER_PAGE = 20
    SALES_PER_PAGE = 10
    PRODUCTS_PER_PAGE = 50
    
    # إعدادات التنبيهات
    LOW_STOCK_THRESHOLD = 5  # الحد الأدنى للمخزون
    
    # إعدادات النسخ الاحتياطي
    BACKUP_FOLDER = 'backups'
    AUTO_BACKUP = False
    BACKUP_INTERVAL_HOURS = 24
    
    # إعدادات العملة (دينار جزائري)
    CURRENCY = "دينار جزائري"
    CURRENCY_SYMBOL = "د.ج"
    
    # إعدادات التاريخ والوقت
    TIMEZONE = 'Africa/Algiers'
    DATE_FORMAT = '%Y-%m-%d'
    TIME_FORMAT = '%H:%M:%S'
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # إعدادات الواجهة
    ITEMS_PER_PAGE = 20
    MAX_SEARCH_RESULTS = 100
    
    # إعدادات الملفات
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xlsx', 'docx', 'doc'}

    # إعدادات الإشعارات
    NOTIFICATIONS_ENABLED = True
    NOTIFICATIONS_CHECK_INTERVAL = 3600  # ساعة واحدة بالثواني
    NOTIFICATIONS_MAX_COUNT = 50  # الحد الأقصى لعدد الإشعارات المحفوظة

    # إعدادات البحث المتقدم
    SEARCH_MAX_RESULTS = 200
    SEARCH_CACHE_TIMEOUT = 300  # 5 دقائق

    # إعدادات التقارير
    REPORTS_CACHE_TIMEOUT = 600  # 10 دقائق
    REPORTS_AUTO_REFRESH = True  # تحديث تلقائي للتقارير

    # إعدادات الأمان
    

class DevelopmentConfig(Config):
    """إعدادات بيئة التطوير"""
    DEBUG = True
    SQLALCHEMY_ECHO = False  # تعيين إلى True لرؤية استعلامات SQL

class ProductionConfig(Config):
    """إعدادات بيئة الإنتاج"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # إعدادات أمان إضافية للإنتاج
    SESSION_COOKIE_SECURE = True  # يجب أن يكون True في بيئة الإنتاج مع HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # إعدادات إضافية للإنتاج
    WTF_CSRF_TIME_LIMIT = None
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

class TestingConfig(Config):
    """إعدادات بيئة الاختبار"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# قاموس الإعدادات
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# إعدادات إضافية للبرنامج
PHONE_BRANDS = [
    'Apple', 'Samsung', 'Xiaomi', 'Huawei', 'Oppo', 'Vivo', 
    'OnePlus', 'Realme', 'Nokia', 'Sony', 'Motorola', 'Honor'
]

STORAGE_OPTIONS = [
    '32GB', '64GB', '128GB', '256GB', '512GB', '1TB'
]

PAYMENT_METHODS = [
    'نقدي', 'بطاقة ائتمان', 'تحويل بنكي', 'آجل', 'فيزا', 'ماستركارد'
]

COLORS = [
    'أسود', 'أبيض', 'ذهبي', 'فضي', 'أزرق', 'أحمر', 'أخضر', 
    'وردي', 'بنفسجي', 'رمادي', 'برونزي', 'تيتانيوم'
]

# رسائل النظام
MESSAGES = {
    'success': {
        'product_added': 'تم إضافة المنتج بنجاح',
        'product_updated': 'تم تحديث المنتج بنجاح',
        'product_deleted': 'تم حذف المنتج بنجاح',
        'customer_added': 'تم إضافة العميل بنجاح',
        'customer_updated': 'تم تحديث العميل بنجاح',
        'customer_deleted': 'تم حذف العميل بنجاح',
        'supplier_added': 'تم إضافة المورد بنجاح',
        'supplier_updated': 'تم تحديث المورد بنجاح',
        'supplier_deleted': 'تم حذف المورد بنجاح',
        'sale_created': 'تم إنشاء الفاتورة بنجاح',
        'backup_created': 'تم إنشاء النسخة الاحتياطية بنجاح'
    },
    'error': {
        'product_not_found': 'المنتج غير موجود',
        'customer_not_found': 'العميل غير موجود',
        'supplier_not_found': 'المورد غير موجود',
        'sale_not_found': 'الفاتورة غير موجودة',
        'insufficient_stock': 'الكمية المطلوبة غير متوفرة في المخزون',
        'invalid_data': 'البيانات المدخلة غير صحيحة',
        'database_error': 'خطأ في قاعدة البيانات',
        'backup_failed': 'فشل في إنشاء النسخة الاحتياطية'
    },
    'warning': {
        'low_stock': 'تحذير: المنتج منخفض المخزون',
        'duplicate_barcode': 'تحذير: الباركود مستخدم من قبل',
        'no_results': 'لا توجد نتائج تطابق البحث'
    }
}