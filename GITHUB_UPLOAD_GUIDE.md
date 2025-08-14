# دليل رفع المشروع على GitHub

## الخطوات المطلوبة:

### 1. إنشاء Repository على GitHub

1. اذهب إلى [GitHub.com](https://github.com)
2. تأكد من تسجيل الدخول بحساب `robotbouba9`
3. انقر على زر "New" أو "+" في الأعلى
4. اختر "New repository"
5. املأ البيانات التالية:
   - **Repository name**: `mobile-store-system`
   - **Description**: `نظام إدارة مخزون محل الهواتف المحمولة - Phone Store Inventory Management System`
   - **Visibility**: اختر Public أو Private حسب رغبتك
   - **⚠️ مهم**: لا تضع علامة على "Add a README file" (لأن لدينا README بالفعل)
   - **⚠️ مهم**: لا تضع علامة على "Add .gitignore" (لأن لدينا .gitignore بالفعل)
   - **⚠️ مهم**: لا تضع علامة على "Choose a license" (لأن لدينا LICENSE بالفعل)
6. انقر "Create repository"

### 2. بعد إنشاء Repository

بعد إنشاء الـ repository، ستظهر لك صفحة بها تعليمات. تجاهل هذه التعليمات واتبع الخطوات التالية:

### 3. رفع المشروع

افتح PowerShell في مجلد المشروع وقم بتشغيل الأوامر التالية:

```powershell
# التأكد من أن remote تم إعداده (تم بالفعل)
git remote -v

# رفع المشروع إلى GitHub
git push -u origin master
```

### 4. إذا طُلب منك تسجيل الدخول

- سيفتح متصفح للمصادقة
- قم بتسجيل الدخول بحساب GitHub الخاص بك
- اقبل الصلاحيات المطلوبة

### 5. التحقق من النجاح

بعد نجاح العملية، ستجد المشروع على الرابط:
https://github.com/robotbouba9/mobile-store-system

## معلومات إضافية

### الملفات التي سيتم رفعها:

- جميع ملفات المشروع
- التوثيق والإرشادات
- ملفات التكوين
- **لن يتم رفع**: قاعدة البيانات، ملفات الكاش، المجلدات المؤقتة (محمية بـ .gitignore)

### فروع Git:

- الفرع الحالي: `master`
- يمكنك إنشاء فروع جديدة لاحقاً للتطوير

### الأوامر المفيدة بعد الرفع:

```powershell
# لرفع تحديثات جديدة
git add .
git commit -m "وصف التحديث"
git push

# لسحب تحديثات من GitHub
git pull

# لعرض حالة المشروع
git status

# لعرض تاريخ التحديثات
git log --oneline
```

## استكشاف الأخطاء

### خطأ "Repository not found"

- تأكد من إنشاء الـ repository على GitHub أولاً
- تأكد من صحة اسم المستخدم واسم الـ repository

### خطأ في المصادقة

- تأكد من تسجيل الدخول في GitHub
- قد تحتاج لإنشاء Personal Access Token للمصادقة

### خطأ في الصلاحيات

- تأكد من أن لديك صلاحيات الكتابة على الـ repository

---

**ملاحظة**: بعد رفع المشروع بنجاح، سيكون متاحاً للجميع (إذا اخترت Public) أو لك فقط (إذا اخترت Private).
