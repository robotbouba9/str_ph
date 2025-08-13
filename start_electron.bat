@echo off
chcp 65001 > nul
title تطبيق Electron - برنامج إدارة مخزون محل الهواتف

echo ================================================
echo تطبيق Electron
echo برنامج إدارة مخزون محل الهواتف
echo ================================================
echo.

:: التحقق من Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js غير مثبت
    echo يرجى تشغيل install_electron.bat أولاً
    pause
    exit /b 1
)

:: التحقق من وجود node_modules
if not exist "node_modules" (
    echo ❌ المكتبات غير مثبتة
    echo يرجى تشغيل install_electron.bat أولاً
    pause
    exit /b 1
)

:: التحقق من Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت
    echo يرجى تثبيت Python من: https://python.org
    pause
    exit /b 1
)

echo ✅ جميع المتطلبات متوفرة
echo.
echo 🚀 تشغيل تطبيق Electron...
echo.

:: تشغيل التطبيق
npm start

if errorlevel 1 (
    echo.
    echo ❌ فشل في تشغيل التطبيق
    echo.
    echo الحلول المقترحة:
    echo 1. تأكد من تثبيت جميع المتطلبات
    echo 2. جرب: npm install
    echo 3. جرب تشغيل الخادم الآمن منفصلاً: start_secure.bat
    echo.
)

pause