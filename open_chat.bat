@echo off
echo 🌐 فتح صفحة الدردشة...
echo =====================

echo 📍 فتح الصفحة من الخادم...
start http://127.0.0.1:5000

timeout /t 2 /nobreak >nul

echo 📁 فتح ملف HTML مباشر...
start "c:\Users\boule\OneDrive\Desktop\str_ph\static\index.html"

echo ✅ تم فتح الصفحات في المتصفح
echo.
echo 💡 نصيحة: تأكد من تشغيل الخادم أولاً باستخدام python app.py
pause