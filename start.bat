@echo off
echo ========================================
echo    متجر الهواتف - Phone Store System
echo ========================================
echo.
echo اختر ما تريد تشغيله:
echo 1. تطبيق الويب (Web Application)
echo 2. بوت التليجرام (Telegram Bot)
echo 3. كلاهما (Both)
echo 4. تثبيت المتطلبات (Install Requirements)
echo 5. خروج (Exit)
echo.
set /p choice="اختر رقم (1-5): "

if "%choice%"=="1" goto web
if "%choice%"=="2" goto bot
if "%choice%"=="3" goto both
if "%choice%"=="4" goto install
if "%choice%"=="5" goto exit

:web
echo تشغيل تطبيق الويب...
python run_web.py
pause
goto menu

:bot
echo تشغيل بوت التليجرام...
python run_bot.py
pause
goto menu

:both
echo تشغيل كلا التطبيقين...
start "Web App" python run_web.py
start "Telegram Bot" python run_bot.py
echo تم تشغيل التطبيقين في نوافذ منفصلة
pause
goto exit

:install
echo تثبيت المتطلبات...
pip install -r requirements.txt
echo تم تثبيت المتطلبات بنجاح!
pause
goto menu

:menu
cls
goto start

:exit
echo شكراً لاستخدام متجر الهواتف!
pause