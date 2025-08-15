@echo off
chcp 65001 > nul
title برنامج إدارة مخزون محل الهواتف المحسن - الإصدار النهائي

cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║    📱 برنامج إدارة مخزون محل الهواتف المحسن 📱              ║
echo ║                                                              ║
echo ║    🌟 المميزات الجديدة:                                      ║
echo ║    ✅ نظام الفئات المتقدم                                    ║
echo ║    ✅ البحث التلقائي الذكي                                   ║
echo ║    ✅ وصف مفصل للمنتجات                                     ║
echo ║    ✅ الأرقام بالتنسيق الإنجليزي                            ║
echo ║    ✅ تصميم محسن ومتناسق                                    ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo 🔧 التحقق من Python...
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت! يرجى تثبيت Python أولاً.
    echo 📥 يمكنك تحميله من: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python متوفر!

if not exist "venv" (
    echo 📦 إنشاء البيئة الافتراضية...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ فشل في إنشاء البيئة الافتراضية!
        pause
        exit /b 1
    )
)

echo 🔧 تفعيل البيئة الافتراضية...
call venv\Scripts\activate.bat

echo 📋 تثبيت المتطلبات...
pip install -r requirements.txt > nul 2>&1
if errorlevel 1 (
    echo ⚠️ تحذير: قد تكون هناك مشكلة في تثبيت المتطلبات
)

echo.
echo ✅ جاهز للتشغيل!
echo.
echo 🌐 سيتم فتح البرنامج تلقائياً في المتصفح
echo 🔧 للإيقاف: اضغط Ctrl+C في هذه النافذة
echo.
echo ════════════════════════════════════════════════════════════════
echo.

set PYTHONIOENCODING=utf-8
python run_final.py

echo.
echo 👋 تم إغلاق البرنامج
pause