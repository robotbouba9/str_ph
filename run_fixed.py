#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل تطبيق الويب لمتجر الهواتف - نسخة مصححة
"""

from flask import Flask
from werkzeug.security import generate_password_hash
from database import db, User, StoreSettings

# Create a new Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///phone_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Create tables and add default admin user
with app.app_context():
    # Create all tables
    db.create_all()
    
    # Create default admin user if it doesn't exist
    if not User.query.filter_by(username='admin').first():
        user = User(
            username='admin',
            password_hash=generate_password_hash('Admin@123'),
            role='admin',
            is_active=True
        )
        db.session.add(user)
        
        # Create default store settings if they don't exist
        if not StoreSettings.query.first():
            settings = StoreSettings()
            db.session.add(settings)
        
        db.session.commit()
        print("✅ تم إنشاء المستخدم الافتراضي (admin/Admin@123)")

# Import the app from the original file
from app import app as original_app

# Copy all routes and configurations from the original app
app.url_map = original_app.url_map
app.view_functions = original_app.view_functions
app.template_folder = original_app.template_folder
app.static_folder = original_app.static_folder
app.config.update(original_app.config)

if __name__ == '__main__':
    print("🚀 بدء تشغيل تطبيق الويب (النسخة المصححة)...")
    print("🌐 يمكنك الوصول للتطبيق على: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)