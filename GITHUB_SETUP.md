# 🚀 رفع المشروع على GitHub

## 📋 **الخطوات المطلوبة:**

### **1. إنشاء مستودع على GitHub**

1. اذهب إلى [GitHub.com](https://github.com)
2. انقر على **"New repository"** أو **"+"** ثم **"New repository"**
3. املأ البيانات التالية:
   - **Repository name**: `phone-store-manager`
   - **Description**: `📱 برنامج إدارة مخزون محل الهواتف - نظام شامل لإدارة المنتجات والمبيعات والعملاء`
   - **Visibility**: اختر **Public** أو **Private** حسب رغبتك
   - **لا تختر** "Add a README file" (لأن لدينا README بالفعل)
   - **لا تختر** "Add .gitignore" (لأن لدينا .gitignore بالفعل)
4. انقر على **"Create repository"**

### **2. ربط المستودع المحلي بـ GitHub**

بعد إنشاء المستودع، ستظهر لك صفحة بتعليمات. استخدم هذه الأوامر:

```bash
# في مجلد المشروع
cd "c:\Users\boule\OneDrive\Desktop\store"

# ربط المستودع المحلي بـ GitHub (استبدل USERNAME بـ اسم المستخدم الخاص بك)
git remote add origin https://github.com/USERNAME/phone-store-manager.git

# رفع الملفات إلى GitHub
git branch -M main
git push -u origin main
```

### **3. التحقق من الرفع**

بعد تنفيذ الأوامر، اذهب إلى صفحة المستودع على GitHub وتأكد من:

- ✅ ظهور جميع الملفات
- ✅ ظهور ملف README.md بشكل صحيح
- ✅ ظهور رسالة الـ commit الأخيرة

---

## 🎯 **بدائل أخرى للرفع:**

### **الطريقة الأولى: GitHub Desktop**

1. حمّل [GitHub Desktop](https://desktop.github.com/)
2. افتح GitHub Desktop
3. انقر على **"Add an Existing Repository from your Hard Drive"**
4. اختر مجلد المشروع: `c:\Users\boule\OneDrive\Desktop\store`
5. انقر على **"Publish repository"**

### **الطريقة الثانية: VS Code**

1. افتح VS Code
2. افتح مجلد المشروع
3. انقر على أيقونة Git في الشريط الجانبي
4. انقر على **"Publish to GitHub"**
5. اختر اسم المستودع والإعدادات

### **الطريقة الثالثة: رفع الملفات يدوياً**

1. اذهب إلى GitHub.com
2. أنشئ مستودع جديد
3. انقر على **"uploading an existing file"**
4. اسحب وأفلت جميع ملفات المشروع

---

## 📁 **الملفات التي سيتم رفعها:**

### **الملفات الرئيسية:**

- ✅ `app.py` - التطبيق الرئيسي
- ✅ `secure_app.py` - التطبيق الآمن
- ✅ `database.py` - نماذج قاعدة البيانات
- ✅ `requirements.txt` - متطلبات Python

### **ملفات التشغيل:**

- ✅ `start_*.bat` - ملفات التشغيل السريع
- ✅ `install_electron.bat` - تثبيت Electron
- ✅ `package.json` - إعدادات Node.js

### **القوالب والواجهات:**

- ✅ `templates/` - جميع قوالب HTML
- ✅ `static/` - الملفات الثابتة (CSS, JS, Images)

### **التوثيق:**

- ✅ `README.md` - دليل المشروع
- ✅ `PRODUCTS_FIX.md` - تقرير الإصلاحات
- ✅ `GITHUB_SETUP.md` - هذا الملف

### **الملفات المُستبعدة (.gitignore):**

- ❌ `__pycache__/` - ملفات Python المؤقتة
- ❌ `*.db` - قواعد البيانات المحلية
- ❌ `node_modules/` - مكتبات Node.js
- ❌ `.vscode/` - إعدادات المحرر

---

## 🎉 **بعد الرفع الناجح:**

### **مشاركة المشروع:**

```
رابط المشروع: https://github.com/USERNAME/phone-store-manager
```

### **تحديث المشروع مستقبلاً:**

```bash
# إضافة تغييرات جديدة
git add .
git commit -m "وصف التحديث"
git push origin main
```

### **استنساخ المشروع على جهاز آخر:**

```bash
git clone https://github.com/USERNAME/phone-store-manager.git
cd phone-store-manager
pip install -r requirements.txt
python app.py
```

---

## 🔧 **نصائح مهمة:**

### **الأمان:**

- ❌ لا ترفع كلمات مرور أو مفاتيح API
- ❌ لا ترفع قواعد بيانات تحتوي على بيانات حقيقية
- ✅ استخدم متغيرات البيئة للمعلومات الحساسة

### **التنظيم:**

- ✅ اكتب رسائل commit واضحة ومفيدة
- ✅ استخدم الـ branches للميزات الجديدة
- ✅ حدّث README.md عند إضافة ميزات جديدة

### **المتابعة:**

- ✅ راجع Issues والـ Pull Requests بانتظام
- ✅ أضف tags للإصدارات المهمة
- ✅ اكتب CHANGELOG للتحديثات الكبيرة

---

## 🎊 **تهانينا!**

بعد اتباع هذه الخطوات، سيكون مشروعك متاحاً على GitHub ويمكن للآخرين:

- 👀 مشاهدة الكود
- 📥 تحميل المشروع
- 🤝 المساهمة في التطوير
- 🐛 الإبلاغ عن الأخطاء
- ⭐ إعطاء نجمة للمشروع

**🚀 مشروعك الآن جاهز للعالم!**
