@echo off
chcp 65001 > nul
title تثبيت تطبيق Electron - برنامج إدارة مخزون محل الهواتف

echo ================================================
echo تثبيت تطبيق Electron
echo برنامج إدارة مخزون محل الهواتف
echo ================================================
echo.

:: التحقق من Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js غير مثبت
    echo.
    echo يرجى تثبيت Node.js من: https://nodejs.org
    echo اختر النسخة LTS (الموصى بها)
    echo.
    pause
    exit /b 1
)

:: التحقق من npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm غير متوفر
    pause
    exit /b 1
)

echo ✅ Node.js متوفر
node --version
echo ✅ npm متوفر  
npm --version
echo.

:: تثبيت المتطلبات
echo 📦 تثبيت مكتبات Electron...
echo.

npm install

if errorlevel 1 (
    echo ❌ فشل في تثبيت المكتبات
    echo.
    echo جاري المحاولة مرة أخرى...
    npm install --force
    
    if errorlevel 1 (
        echo ❌ فشل نهائي في التثبيت
        echo.
        echo الحلول المقترحة:
        echo 1. تأكد من اتصال الإنترنت
        echo 2. جرب: npm cache clean --force
        echo 3. جرب: npm install --legacy-peer-deps
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ✅ تم تثبيت جميع المكتبات بنجاح!
echo.

:: تثبيت المتطلبات الآمنة لـ Python
echo 📦 تثبيت متطلبات Python الآمنة...
pip install -r requirements_secure.txt --quiet --user

echo.
echo 🎉 التثبيت مكتمل!
echo.
echo للتشغيل:
echo - تطبيق Electron: npm start
echo - أو: start_electron.bat
echo.

pause