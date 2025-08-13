@echo off
chcp 65001 > nul
title برنامج إدارة مخزون محل الهواتف

echo ================================================
echo برنامج إدارة مخزون محل الهواتف
echo ================================================
echo.

:: التحقق من وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo خطأ: Python غير مثبت على النظام
    echo يرجى تثبيت Python 3.7 أو أحدث من: https://python.org
    pause
    exit /b 1
)

:: التحقق من وجود pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo خطأ: pip غير متوفر
    echo يرجى إعادة تثبيت Python مع pip
    pause
    exit /b 1
)

:: تثبيت المتطلبات إذا لم تكن مثبتة
echo جاري التحقق من المتطلبات...
pip install -r requirements.txt --quiet --user

if errorlevel 1 (
    echo تحذير: قد تكون بعض المكتبات غير مثبتة بشكل صحيح
    echo سيتم المحاولة مرة أخرى...
    pip install Flask Flask-SQLAlchemy --user
)

echo.
echo تم التحقق من المتطلبات بنجاح
echo.

:: تشغيل البرنامج
echo جاري تشغيل البرنامج...
echo يمكنك إغلاق هذه النافذة بعد فتح البرنامج
echo.

python desktop_app.py

if errorlevel 1 (
    echo.
    echo حدث خطأ في تشغيل البرنامج
    echo جاري المحاولة بالطريقة البديلة...
    echo.
    python run.py
)

pause