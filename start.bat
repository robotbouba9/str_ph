@echo off
chcp 65001 > nul
title برنامج إدارة مخزون محل الهواتف المحسن

echo.
echo ========================================
echo    برنامج إدارة مخزون محل الهواتف المحسن
echo ========================================
echo.
echo 🚀 بدء تشغيل البرنامج...
echo.

cd /d "%~dp0"

if not exist "venv" (
    echo 📦 إنشاء البيئة الافتراضية...
    python -m venv venv
)

echo 🔧 تفعيل البيئة الافتراضية...
call venv\Scripts\activate.bat

echo 📋 تثبيت المتطلبات...
pip install -r requirements.txt > nul 2>&1

echo.
echo ✅ جاهز للتشغيل!
echo.
echo 🌐 سيتم فتح البرنامج على: http://127.0.0.1:5000
echo 🔧 للإيقاف: اضغط Ctrl+C
echo.

python run_enhanced.py

pause