@echo off
chcp 65001 > nul
title برنامج إدارة مخزون محل الهواتف - الخادم الآمن

echo ================================================
echo برنامج إدارة مخزون محل الهواتف
echo الخادم الآمن للإنتاج
echo ================================================
echo.

:: التحقق من Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ خطأ: Python غير مثبت
    pause
    exit /b 1
)

:: تثبيت المتطلبات الآمنة
echo 📦 تثبيت المتطلبات الآمنة...
pip install -r requirements_secure.txt --quiet --user

if errorlevel 1 (
    echo ⚠️ تحذير: قد تكون بعض المكتبات غير مثبتة
    pip install waitress flask-wtf --user
)

echo.
echo 🔒 تشغيل الخادم الآمن...
echo 🌐 الرابط: http://localhost:5000
echo ⏹️  لإيقاف الخادم: اضغط Ctrl+C
echo.

python secure_app.py

pause