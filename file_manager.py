#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
نظام إدارة الملفات للمساعد البرمجي
يتيح للمساعد قراءة وتعديل الملفات مباشرة
"""

import os
import json
import shutil
from datetime import datetime
import re

class FileManager:
    def __init__(self, project_root="c:/Users/boule/OneDrive/Desktop/str_ph"):
        self.project_root = project_root.replace("\\", "/")
        self.allowed_extensions = ['.py', '.html', '.css', '.js', '.json', '.txt', '.md', '.sql']
        self.backup_dir = os.path.join(project_root, 'backups')
        self.ensure_backup_dir()
    
    def ensure_backup_dir(self):
        """إنشاء مجلد النسخ الاحتياطية إذا لم يكن موجوداً"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def is_safe_path(self, file_path):
        """التحقق من أن المسار آمن ومسموح"""
        # تحويل المسار إلى مسار مطلق
        abs_path = os.path.abspath(file_path)
        project_abs = os.path.abspath(self.project_root)
        
        # التأكد أن الملف داخل مجلد المشروع
        if not abs_path.startswith(project_abs):
            return False
        
        # التحقق من امتداد الملف
        _, ext = os.path.splitext(abs_path)
        if ext not in self.allowed_extensions:
            return False
        
        # منع الوصول لملفات النظام الحساسة
        forbidden_files = ['config.py', 'database.py', '.env']
        filename = os.path.basename(abs_path)
        if filename in forbidden_files:
            return False
        
        return True
    
    def create_backup(self, file_path):
        """إنشاء نسخة احتياطية من الملف"""
        if not os.path.exists(file_path):
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        backup_name = f"{filename}_{timestamp}.backup"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
    
    def read_file(self, file_path):
        """قراءة محتوى الملف"""
        # إذا كان المسار نسبي، اجعله مطلق
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.project_root, file_path)
            
        if not self.is_safe_path(file_path):
            return {"error": "مسار الملف غير مسموح أو غير آمن"}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "path": file_path,
                "size": len(content),
                "lines": len(content.split('\n'))
            }
        except Exception as e:
            return {"error": f"خطأ في قراءة الملف: {str(e)}"}
    
    def write_file(self, file_path, content, create_backup=True):
        """كتابة محتوى إلى الملف"""
        # إذا كان المسار نسبي، اجعله مطلق
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.project_root, file_path)
            
        if not self.is_safe_path(file_path):
            return {"error": "مسار الملف غير مسموح أو غير آمن"}
        
        try:
            # إنشاء نسخة احتياطية إذا كان الملف موجوداً
            backup_path = None
            if create_backup and os.path.exists(file_path):
                backup_path = self.create_backup(file_path)
            
            # كتابة المحتوى الجديد
            dir_path = os.path.dirname(file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "path": file_path,
                "backup": backup_path,
                "size": len(content),
                "message": "تم حفظ الملف بنجاح"
            }
        except Exception as e:
            return {"error": f"خطأ في كتابة الملف: {str(e)}"}
    
    def edit_file(self, file_path, old_text, new_text, line_number=None):
        """تعديل جزء محدد من الملف"""
        if not self.is_safe_path(file_path):
            return {"error": "مسار الملف غير مسموح أو غير آمن"}
        
        # قراءة الملف الحالي
        read_result = self.read_file(file_path)
        if "error" in read_result:
            return read_result
        
        content = read_result["content"]
        
        try:
            # إنشاء نسخة احتياطية
            backup_path = self.create_backup(file_path)
            
            # تطبيق التعديل
            if line_number is not None:
                # تعديل سطر محدد
                lines = content.split('\n')
                if 0 <= line_number < len(lines):
                    lines[line_number] = new_text
                    new_content = '\n'.join(lines)
                else:
                    return {"error": f"رقم السطر {line_number} غير صحيح"}
            else:
                # استبدال النص
                if old_text in content:
                    new_content = content.replace(old_text, new_text)
                else:
                    return {"error": "النص المطلوب استبداله غير موجود"}
            
            # حفظ التعديلات
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return {
                "success": True,
                "path": file_path,
                "backup": backup_path,
                "changes": len(new_content) - len(content),
                "message": "تم تعديل الملف بنجاح"
            }
        except Exception as e:
            return {"error": f"خطأ في تعديل الملف: {str(e)}"}
    
    def list_files(self, directory=None, pattern=None):
        """عرض قائمة الملفات في المجلد"""
        if directory is None:
            directory = self.project_root
        
        if not self.is_safe_path(os.path.join(directory, "dummy.py")):
            return {"error": "مسار المجلد غير مسموح"}
        
        try:
            files = []
            for root, dirs, filenames in os.walk(directory):
                # تجاهل مجلدات معينة
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'node_modules']]
                
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    _, ext = os.path.splitext(filename)
                    
                    if ext in self.allowed_extensions:
                        if pattern is None or re.search(pattern, filename, re.IGNORECASE):
                            rel_path = os.path.relpath(file_path, self.project_root)
                            files.append({
                                "name": filename,
                                "path": rel_path,
                                "full_path": file_path,
                                "extension": ext,
                                "size": os.path.getsize(file_path)
                            })
            
            return {"success": True, "files": files, "count": len(files)}
        except Exception as e:
            return {"error": f"خطأ في عرض الملفات: {str(e)}"}
    
    def create_file(self, file_path, content="", template=None):
        """إنشاء ملف جديد"""
        # إذا كان المسار نسبي، اجعله مطلق
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.project_root, file_path)
        
        if not self.is_safe_path(file_path):
            return {"error": "مسار الملف غير مسموح أو غير آمن"}
        
        if os.path.exists(file_path):
            return {"error": "الملف موجود بالفعل"}
        
        try:
            # استخدام قالب إذا تم تحديده
            if template:
                content = self.get_template(template, file_path)
            
            # إنشاء المجلد إذا لم يكن موجوداً
            dir_path = os.path.dirname(file_path)
            if dir_path:  # تأكد من وجود مسار المجلد
                os.makedirs(dir_path, exist_ok=True)
            
            # إنشاء الملف
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "path": file_path,
                "size": len(content),
                "message": "تم إنشاء الملف بنجاح"
            }
        except Exception as e:
            return {"error": f"خطأ في إنشاء الملف: {str(e)}"}
    
    def get_template(self, template_type, file_path):
        """الحصول على قالب للملف الجديد"""
        filename = os.path.basename(file_path)
        
        templates = {
            "python": f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
{filename} - وصف الملف
"""

def main():
    """الدالة الرئيسية"""
    pass

if __name__ == "__main__":
    main()
''',
            "html": f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{filename}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h1>صفحة جديدة</h1>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
''',
            "css": f'''/* {filename} - ملف الأنماط */

body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    direction: rtl;
    text-align: right;
}}
''',
            "js": f'''// {filename} - ملف JavaScript

document.addEventListener('DOMContentLoaded', function() {{
    console.log('تم تحميل الصفحة');
}});
'''
        }
        
        return templates.get(template_type, "")
    
    def get_file_info(self, file_path):
        """الحصول على معلومات الملف"""
        if not self.is_safe_path(file_path):
            return {"error": "مسار الملف غير مسموح أو غير آمن"}
        
        if not os.path.exists(file_path):
            return {"error": "الملف غير موجود"}
        
        try:
            stat = os.stat(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "path": file_path,
                "size": stat.st_size,
                "lines": len(content.split('\n')),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": os.path.splitext(file_path)[1],
                "encoding": "utf-8"
            }
        except Exception as e:
            return {"error": f"خطأ في الحصول على معلومات الملف: {str(e)}"}