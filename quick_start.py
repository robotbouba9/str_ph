#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل سريع للتطبيق مع إعداد أولي
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """Vérifier la version de Python"""
    # Ajouter le code pour vérifier la version de Python ici
    pass

def check_virtual_env():
    """Vérifier l'environnement virtuel"""
    # Ajouter le code pour vérifier l'environnement virtuel ici
    pass

def install_requirements():
    """Installer les dépendances"""
    # Ajouter le code pour installer les dépendances ici
    return True

def setup_env():
    """Configurer l'environnement"""
    # Ajouter le code pour configurer l'environnement ici
    pass

def create_directories():
    """إنشاء المجلدات المطلوبة"""
    directories = ['instance', 'uploads', 'cache', 'backups', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

    check_python_version()
    check_virtual_env()
    if install_requirements():
        setup_env()
    if '--auto-commits' in sys.argv:
        print("✅ Auto-commits activés")
        # Ajouter le code pour les auto-commits ici
    create_directories()
    print("✅ تم إنشاء المجلدات المطلوبة")
    try:
        from app import app
        print("\n🌐 التطبيق يعمل على: http://localhost:5000")
        print("👤 المستخدم الافتراضي: owner")
        print("🔑 كلمة المرور الافتراضية: Owner@123")
        print("💡 زر /init_database لإنشاء قاعدة البيانات")
        print("=" * 50)
        
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل التطبيق: {e}")
        sys.exit(1)
