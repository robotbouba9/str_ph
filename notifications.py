# -*- coding: utf-8 -*-
"""
نظام الإشعارات لبرنامج إدارة مخزون محل الهواتف
"""

from datetime import datetime
import sqlite3
import os
from database import db, Product, StoreSettings
from flask import current_app

class NotificationManager:
    """مدير الإشعارات في النظام"""

    def __init__(self):
        self.notifications = []

    def check_low_stock(self):
        """فحص المنتجات منخفضة المخزون وإضافة إشعارات"""
        try:
            low_stock_products = Product.query.filter(
                Product.quantity <= Product.min_quantity
            ).all()

            notifications = []
            for product in low_stock_products:
                notification = {
                    'id': len(self.notifications) + 1,
                    'type': 'low_stock',
                    'title': f'منتج منخفض المخزون: {product.name}',
                    'message': f'الكمية المتوفرة: {product.quantity} الحد الأدنى: {product.min_quantity}',
                    'product_id': product.id,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'read': False
                }
                notifications.append(notification)

            self.notifications.extend(notifications)
            return notifications
        except Exception as e:
            print(f"خطأ في فحص المخزون المنخفض: {e}")
            return []

    def get_notifications(self, unread_only=False):
        """الحصول على قائمة الإشعارات"""
        if unread_only:
            return [n for n in self.notifications if not n['read']]
        return self.notifications

    def mark_as_read(self, notification_id):
        """تحييد إشعار كمقروء"""
        for notification in self.notifications:
            if notification['id'] == notification_id:
                notification['read'] = True
                return True
        return False

    def clear_all(self):
        """مسح جميع الإشعارات"""
        self.notifications = []

    def save_to_database(self, user_id):
        """حفظ الإشعارات في قاعدة البيانات للمستخدم"""
        try:
            # التحقق من وجود جدول الإشعارات
            if not hasattr(db.Model, '_get_table_name'):
                return False

            notifications_table_name = 'notifications'

            # التحقق من وجود الجدول
            inspector = db.inspect(db.engine)
            if notifications_table_name not in inspector.get_table_names():
                # إنشاء الجدول إذا لم يكن موجودًا
                sql = """
                CREATE TABLE notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    type TEXT,
                    title TEXT,
                    message TEXT,
                    product_id INTEGER,
                    timestamp DATETIME,
                    read BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
                """
                db.session.execute(sql)
                db.session.commit()

            # حفظ الإشعارات غير المقروءة
            for notification in self.notifications:
                if not notification['read']:
                    sql = """
                    INSERT INTO notifications (user_id, type, title, message, product_id, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """
                    db.session.execute(sql, (
                        user_id,
                        notification['type'],
                        notification['title'],
                        notification['message'],
                        notification['product_id'],
                        notification['timestamp']
                    ))

            db.session.commit()
            return True
        except Exception as e:
            print(f"خطأ في حفظ الإشعارات: {e}")
            db.session.rollback()
            return False

    def load_from_database(self, user_id):
        """تحميل الإشعارات من قاعدة البيانات"""
        try:
            notifications_table_name = 'notifications'

            # التحقق من وجود الجدول
            inspector = db.inspect(db.engine)
            if notifications_table_name not in inspector.get_table_names():
                return False

            sql = """
            SELECT id, type, title, message, product_id, timestamp, read
            FROM notifications
            WHERE user_id = ?
            ORDER BY timestamp DESC
            """
            results = db.session.execute(sql, (user_id,)).fetchall()

            notifications = []
            for row in results:
                notification = {
                    'id': row[0],
                    'type': row[1],
                    'title': row[2],
                    'message': row[3],
                    'product_id': row[4],
                    'timestamp': row[5],
                    'read': bool(row[6])
                }
                notifications.append(notification)

            self.notifications = notifications
            return True
        except Exception as e:
            print(f"خطأ في تحميل الإشعارات: {e}")
            return False

# إنشاء مثيل مدير الإشعارات
notification_manager = NotificationManager()
