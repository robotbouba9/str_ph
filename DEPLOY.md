# 🚀 دليل النشر على Render

## خطوات النشر

### 1. إعداد المستودع

تأكد من أن جميع الملفات محدثة في GitHub:

```bash
git add .
git commit -m "Update for deployment"
git push origin master
```

### 2. إنشاء خدمة Render

1. **تسجيل الدخول إلى Render:**

   - اذهب إلى [render.com](https://render.com)
   - سجل دخولك أو أنشئ حساب جديد

2. **إنشاء Web Service:**

   - اضغط "New" → "Web Service"
   - اختر "Build and deploy from a Git repository"
   - اربط حساب GitHub الخاص بك
   - اختر مستودع `store-`

3. **إعدادات الخدمة:**
   ```
   Name: store-web
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 app:app
   ```

### 3. إنشاء قاعدة البيانات PostgreSQL

1. **إنشاء Database:**

   - اضغط "New" → "PostgreSQL"
   - اختر الخطة المجانية
   - اسم قاعدة البيانات: `store-db`

2. **الحصول على رابط الاتصال:**
   - انسخ `External Database URL`
   - سيكون بالشكل: `postgres://username:password@host:port/database`

### 4. إعداد متغيرات البيئة

في إعدادات Web Service، أضف:

```env
APP_ENV=production
SECRET_KEY=your-generated-secret-key
DATABASE_URL=postgresql://your-database-url
```

**ملاحظة:** Render سينشئ `SECRET_KEY` تلقائياً إذا لم تحدده.

### 5. ربط قاعدة البيانات بالتطبيق

في إعدادات Web Service:

1. اذهب إلى "Environment"
2. أضف متغير `DATABASE_URL`
3. اختر "Add from Database" → اختر `store-db`

### 6. النشر

1. **النشر التلقائي:**

   - Render سينشر التطبيق تلقائياً
   - راقب سجلات البناء في "Logs"

2. **إنشاء الجداول:**
   - بعد النشر الناجح، ستُنشأ الجداول تلقائياً
   - سيُنشأ مستخدم admin افتراضي

### 7. الوصول للتطبيق

- الرابط سيكون: `https://your-service-name.onrender.com`
- بيانات الدخول الافتراضية:
  - اسم المستخدم: `admin`
  - كلمة المرور: `Admin@123`

## استكشاف الأخطاء

### مشاكل شائعة وحلولها

#### 1. خطأ في البناء (Build Error)

```bash
# تحقق من requirements.txt
pip install -r requirements.txt

# تحقق من إصدار Python
python --version
```

#### 2. خطأ في قاعدة البيانات

- تأكد من صحة `DATABASE_URL`
- تحقق من اتصال قاعدة البيانات
- راجع سجلات الأخطاء

#### 3. خطأ في التطبيق

```bash
# تحقق من السجلات
# في Render Dashboard → Service → Logs
```

#### 4. مشاكل الذاكرة

- الخطة المجانية محدودة الذاكرة
- قلل عدد العمليات المتزامنة
- استخدم `--workers 1` إذا لزم الأمر

### نصائح للأداء

1. **تحسين قاعدة البيانات:**

   ```python
   # في config.py
   SQLALCHEMY_ENGINE_OPTIONS = {
       'pool_pre_ping': True,
       'pool_recycle': 300,
   }
   ```

2. **ضغط الملفات الثابتة:**

   - استخدم CDN للملفات الكبيرة
   - ضغط CSS و JavaScript

3. **تحسين الاستعلامات:**
   - استخدم الفهرسة المناسبة
   - تجنب الاستعلامات المعقدة

## التحديثات التلقائية

### إعداد Auto-Deploy

1. في إعدادات Render Service
2. فعّل "Auto-Deploy"
3. اختر branch `master`

### عملية التحديث

```bash
# محلياً
git add .
git commit -m "Update feature"
git push origin master

# Render سينشر تلقائياً
```

## النسخ الاحتياطي

### نسخ احتياطي لقاعدة البيانات

```bash
# تصدير البيانات
pg_dump $DATABASE_URL > backup.sql

# استيراد البيانات
psql $DATABASE_URL < backup.sql
```

### نسخ احتياطي للملفات

- الملفات المرفوعة في مجلد `uploads`
- استخدم خدمة تخزين خارجية للملفات الكبيرة

## المراقبة

### مراقبة الأداء

- استخدم Render Metrics
- راقب استخدام الذاكرة والمعالج
- تتبع أوقات الاستجابة

### السجلات

```bash
# عرض السجلات المباشرة
# في Render Dashboard → Logs
```

## الأمان

### إعدادات الأمان

```python
# في config.py للإنتاج
SESSION_COOKIE_SECURE = True  # للـ HTTPS فقط
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

### حماية البيانات

- استخدم HTTPS دائماً
- احم متغيرات البيئة الحساسة
- راجع الصلاحيات بانتظام

---

**للمساعدة الإضافية، راجع [وثائق Render](https://render.com/docs)**
