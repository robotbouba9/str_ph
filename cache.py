# -*- coding: utf-8 -*-
"""
نظام التخزين المؤقت لتحسين أداء النظام
"""

import time
import hashlib
import json
import os
from datetime import datetime, timedelta
from functools import wraps
from config import Config

class CacheManager:
    """مدير التخزين المؤقت للبيانات"""

    def __init__(self, cache_dir='cache', default_timeout=300):
        """
        تهيئة مدير التخزين المؤقت

        :param cache_dir: مسار مجلد التخزين المؤقت
        :param default_timeout: وقت انتهاء الصلاحية الافتراضي بالثواني
        """
        self.cache_dir = cache_dir
        self.default_timeout = default_timeout

        # إنشاء مجلد التخزين المؤقت إذا لم يكن موجودًا
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def _get_cache_path(self, key):
        """الحصول على مسار ملف التخزين المؤقت بناءً على المفتاح"""
        # إنشاء تجزئة فريدة للمفتاح
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.cache")

    def set(self, key, value, timeout=None):
        """
        حفظ قيمة في التخزين المؤقت

        :param key: مفتاح التخزين المؤقت
        :param value: القيمة المراد حفظها
        :param timeout: وقت انتهاء الصلاحية بالثواني (إذا لم يتم تحديده، سيتم استخدام القيمة الافتراضية)
        :return: True إذا تم الحفظ بنجاح، False في حالة الخطأ
        """
        try:
            # تحديد وقت انتهاء الصلاحية
            expire_time = time.time() + (timeout if timeout is not None else self.default_timeout)

            # إنشاء بيانات التخزين المؤقت
            cache_data = {
                'value': value,
                'expire': expire_time,
                'created_at': time.time()
            }

            # الحصول على مسار ملف التخزين المؤقت
            cache_path = self._get_cache_path(key)

            # حفظ البيانات في ملف
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"خطأ في حفظ التخزين المؤقت: {e}")
            return False

    def get(self, key):
        """
        الحصول على قيمة من التخزين المؤقت

        :param key: مفتاح التخزين المؤقت
        :return: القيمة إذا كانت موجودة وصالحة، None إذا كانت منتهية الصلاحية أو غير موجودة
        """
        try:
            # الحصول على مسار ملف التخزين المؤقت
            cache_path = self._get_cache_path(key)

            # التحقق من وجود الملف
            if not os.path.exists(cache_path):
                return None

            # قراءة البيانات من الملف
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # التحقق من انتهاء الصلاحية
            if cache_data['expire'] < time.time():
                # حذف الملف منتهي الصلاحية
                os.remove(cache_path)
                return None

            return cache_data['value']
        except Exception as e:
            print(f"خطأ في قراءة التخزين المؤقت: {e}")
            return None

    def delete(self, key):
        """
        حذف قيمة من التخزين المؤقت

        :param key: مفتاح التخزين المؤقت
        :return: True إذا تم الحذف بنجاح، False في حالة الخطأ
        """
        try:
            # الحصول على مسار ملف التخزين المؤقت
            cache_path = self._get_cache_path(key)

            # التحقق من وجود الملف
            if not os.path.exists(cache_path):
                return False

            # حذف الملف
            os.remove(cache_path)
            return True
        except Exception as e:
            print(f"خطأ في حذف التخزين المؤقت: {e}")
            return False

    def clear(self):
        """
        مسح جميع البيانات من التخزين المؤقت

        :return: عدد الملفات المحذفة
        """
        try:
            count = 0
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    os.remove(os.path.join(self.cache_dir, filename))
                    count += 1
            return count
        except Exception as e:
            print(f"خطأ في مسح التخزين المؤقت: {e}")
            return 0

    def cleanup(self):
        """
        مسح جميع الملفات منتهية الصلاحية من التخزين المؤقت

        :return: عدد الملفات المحذفة
        """
        try:
            count = 0
            current_time = time.time()

            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    cache_path = os.path.join(self.cache_dir, filename)

                    try:
                        # قراءة وقت انتهاء الصلاحية
                        with open(cache_path, 'r', encoding='utf-8') as f:
                            cache_data = json.load(f)

                        # حذف الملفات منتهية الصلاحية
                        if cache_data['expire'] < current_time:
                            os.remove(cache_path)
                            count += 1
                    except:
                        # في حالة وجود مشكلة في الملف، نقوم بحذفه
                        os.remove(cache_path)
                        count += 1

            return count
        except Exception as e:
            print(f"خطأ في تنظيف التخزين المؤقت: {e}")
            return 0

def cached(timeout=None, key_prefix='cache'):
    """
    منشئ الديكور لتخزين مؤقت للدوال

    :param timeout: وقت انتهاء الصلاحية بالثواني
    :param key_prefix: بادئة مفتاح التخزين المؤقت
    :return: دالة الديكور
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # إنشاء مدير التخزين المؤقت
            cache_manager = CacheManager()

            # إنشاء مفتاح فريد للدالة والوسائط
            func_args = str(args) + str(sorted(kwargs.items()))
            key = f"{key_prefix}:{func.__name__}:{hashlib.md5(func_args.encode()).hexdigest()}"

            # محاولة الحصول على النتيجة من التخزين المؤقت
            cached_result = cache_manager.get(key)
            if cached_result is not None:
                return cached_result

            # تنفيذ الدالة إذا لم تكن النتيجة في التخزين المؤقت
            result = func(*args, **kwargs)

            # حفظ النتيجة في التخزين المؤقت
            cache_manager.set(key, result, timeout)

            return result
        return wrapper
    return decorator

# إنشاء مثيل مدير التخزين المؤقت
cache_manager = CacheManager()
