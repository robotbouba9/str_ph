#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
خادم Groq منفصل للاتصال المباشر مع static/index.html
"""

import os
import subprocess
import json
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

# تحميل متغيرات البيئة
load_dotenv()

# مسار المشروع
PROJECT_PATH = Path(r"c:\Users\boule\OneDrive\Desktop\str_ph")

# التحقق من API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("❌ لم يتم العثور على GROQ_API_KEY في ملف .env")

# إنشاء عميل Groq
client = Groq(api_key=api_key)

# وظائف مساعدة
def read_project_file(file_path):
    """قراءة ملف من المشروع"""
    try:
        full_path = PROJECT_PATH / file_path
        if not full_path.exists():
            return None, f"الملف غير موجود: {file_path}"
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content, None
    except Exception as e:
        return None, f"خطأ في قراءة الملف: {str(e)}"

def write_project_file(file_path, content):
    """كتابة ملف في المشروع"""
    try:
        full_path = PROJECT_PATH / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, None
    except Exception as e:
        return False, f"خطأ في كتابة الملف: {str(e)}"

def list_project_files(directory=""):
    """عرض ملفات المشروع"""
    try:
        path = PROJECT_PATH / directory if directory else PROJECT_PATH
        if not path.exists():
            return [], f"المجلد غير موجود: {directory}"
        
        files = []
        for item in path.iterdir():
            if item.name.startswith('.'):
                continue
            files.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "path": str(item.relative_to(PROJECT_PATH)).replace('\\', '/'),
                "size": item.stat().st_size if item.is_file() else 0
            })
        
        return sorted(files, key=lambda x: (x['type'] == 'file', x['name'])), None
    except Exception as e:
        return [], f"خطأ في عرض الملفات: {str(e)}"

def execute_command(command):
    """تنفيذ أمر في النظام"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=PROJECT_PATH,
            capture_output=True, 
            text=True, 
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": "انتهت مهلة تنفيذ الأمر",
            "return_code": -1
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": f"خطأ في تنفيذ الأمر: {str(e)}",
            "return_code": -1
        }

def process_special_commands(message):
    """معالجة الأوامر الخاصة في الرسالة"""
    import re
    
    # أوامر قراءة الملفات
    read_pattern = r"اقرأ ملف (.+)"
    match = re.search(read_pattern, message)
    if match:
        file_path = match.group(1).strip()
        content, error = read_project_file(file_path)
        if error:
            return message + f"\n\n❌ خطأ: {error}"
        else:
            return message + f"\n\n📄 محتوى الملف {file_path}:\n```\n{content}\n```"
    
    # أوامر عرض الملفات
    list_pattern = r"اعرض ملفات(?:\s+(.+))?"
    match = re.search(list_pattern, message)
    if match:
        directory = match.group(1).strip() if match.group(1) else ""
        files, error = list_project_files(directory)
        if error:
            return message + f"\n\n❌ خطأ: {error}"
        else:
            files_list = "\n".join([f"{'📁' if f['type'] == 'directory' else '📄'} {f['name']}" for f in files])
            return message + f"\n\n📂 ملفات المجلد {directory or 'الجذر'}:\n{files_list}"
    
    # أوامر تنفيذ الأوامر
    cmd_pattern = r"نفذ أمر (.+)"
    match = re.search(cmd_pattern, message)
    if match:
        command = match.group(1).strip()
        result = execute_command(command)
        status = "✅" if result["success"] else "❌"
        output = result["output"] if result["output"] else "لا يوجد مخرجات"
        error = result["error"] if result["error"] else ""
        return message + f"\n\n{status} نتيجة تنفيذ الأمر: {command}\n📤 المخرجات:\n{output}\n{'⚠️ أخطاء:\n' + error if error else ''}"
    
    return message

# تطبيق Flask بسيط
app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)  # تفعيل CORS للسماح بالاتصال من المتصفح

@app.route("/ask", methods=["POST"])
def ask():
    """API endpoint للتفاعل مع Groq AI"""
    try:
        data = request.json
        if not data or not data.get("message"):
            return jsonify({"reply": "❌ الرجاء إرسال رسالة"}), 400
        
        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"reply": "❌ الرجاء إرسال رسالة غير فارغة"}), 400

        print(f"📨 رسالة من المستخدم: {user_message}")

        # معالجة الأوامر الخاصة
        processed_message = process_special_commands(user_message)

        # إرسال الرسالة إلى Groq
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system", 
                    "content": """أنت مساعد برمجي ذكي متخصص في مشروع إدارة مخزون محل الهواتف المحمولة. 

المشروع مبني بـ:
- Flask (Python) كإطار العمل الرئيسي
- SQLAlchemy لقاعدة البيانات
- Jinja2 للقوالب
- Bootstrap للواجهات
- JavaScript للتفاعل

الملفات الرئيسية:
- app.py: التطبيق الرئيسي وجميع المسارات
- database.py: نماذج قاعدة البيانات
- config.py: إعدادات التطبيق
- forms.py: نماذج WTForms
- templates/: قوالب HTML
- static/: ملفات CSS/JS/الصور

وظائف النظام:
- إدارة المنتجات والعملاء والموردين
- نظام المبيعات والفواتير
- إدارة المخزون والمرتجعات
- تقارير وإحصائيات
- تصدير Excel وطباعة حرارية

قدراتك الخاصة:
- قراءة ملفات المشروع: استخدم "اقرأ ملف [مسار الملف]"
- تعديل الملفات: استخدم "عدل ملف [مسار] بالمحتوى [المحتوى]"
- عرض الملفات: استخدم "اعرض ملفات [مجلد]"
- تنفيذ أوامر: استخدم "نفذ أمر [الأمر]"

تجيب باللغة العربية وتساعد في:
- تحليل وفهم الكود
- اقتراح تحسينات
- حل المشاكل البرمجية
- إضافة ميزات جديدة
- شرح كيفية عمل الأجزاء المختلفة
- مراجعة الكود وأفضل الممارسات
- تعديل الملفات مباشرة
- تنفيذ أوامر النظام

عندما يطلب المستخدم تعديل ملف أو تنفيذ أمر، استخدم الأوامر المخصصة أعلاه."""
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            max_tokens=2000,
            temperature=0.3
        )

        ai_reply = response.choices[0].message.content
        print(f"🤖 رد الذكاء الاصطناعي: {ai_reply}")
        
        return jsonify({"reply": ai_reply})

    except Exception as e:
        error_msg = f"❌ حدث خطأ في الخدمة: {str(e)}"
        print(f"🚨 خطأ: {error_msg}")
        return jsonify({"reply": error_msg}), 500

@app.route("/")
def home():
    """عرض صفحة الدردشة"""
    return app.send_static_file("index.html")

@app.route("/analyze", methods=["POST"])
def analyze_code():
    """تحليل ملف أو كود برمجي"""
    try:
        data = request.json
        if not data:
            return jsonify({"reply": "❌ الرجاء إرسال بيانات للتحليل"}), 400
        
        file_path = data.get("file_path", "")
        code_content = data.get("code", "")
        analysis_type = data.get("type", "general")  # general, security, performance, structure
        
        if not code_content and file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code_content = f.read()
            except Exception as e:
                return jsonify({"reply": f"❌ لا يمكن قراءة الملف: {str(e)}"}), 400
        
        if not code_content:
            return jsonify({"reply": "❌ لم يتم تقديم كود للتحليل"}), 400

        analysis_prompts = {
            "general": "قم بتحليل هذا الكود وقدم ملاحظات عامة حول جودته وطريقة تحسينه:",
            "security": "قم بمراجعة هذا الكود من ناحية الأمان وحدد المشاكل الأمنية المحتملة:",
            "performance": "قم بتحليل أداء هذا الكود واقترح تحسينات للسرعة والكفاءة:",
            "structure": "قم بمراجعة بنية وتنظيم هذا الكود واقترح تحسينات معمارية:"
        }
        
        prompt = analysis_prompts.get(analysis_type, analysis_prompts["general"])
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system", 
                    "content": """أنت خبير في مراجعة الكود البرمجي. تحلل الكود بعمق وتقدم اقتراحات مفيدة.
                    ركز على:
                    - جودة الكود وقابليته للقراءة
                    - الأمان والثغرات المحتملة
                    - الأداء والكفاءة
                    - أفضل الممارسات
                    - التحسينات المقترحة
                    
                    اجعل تحليلك مفصلاً ومفيداً للمطور."""
                },
                {
                    "role": "user", 
                    "content": f"{prompt}\n\n```\n{code_content}\n```"
                }
            ],
            max_tokens=3000,
            temperature=0.2
        )

        analysis = response.choices[0].message.content
        return jsonify({
            "analysis": analysis,
            "type": analysis_type,
            "file_path": file_path
        })

    except Exception as e:
        return jsonify({"reply": f"❌ خطأ في التحليل: {str(e)}"}), 500

@app.route("/files", methods=["GET"])
def get_files():
    """عرض ملفات المشروع"""
    try:
        directory = request.args.get("dir", "")
        files, error = list_project_files(directory)
        
        if error:
            return jsonify({"error": error}), 400
        
        return jsonify({"files": files, "directory": directory})
    
    except Exception as e:
        return jsonify({"error": f"خطأ في عرض الملفات: {str(e)}"}), 500

@app.route("/file", methods=["GET"])
def get_file():
    """قراءة ملف من المشروع"""
    try:
        file_path = request.args.get("path")
        if not file_path:
            return jsonify({"error": "مسار الملف مطلوب"}), 400
        
        content, error = read_project_file(file_path)
        
        if error:
            return jsonify({"error": error}), 400
        
        return jsonify({"content": content, "path": file_path})
    
    except Exception as e:
        return jsonify({"error": f"خطأ في قراءة الملف: {str(e)}"}), 500

@app.route("/file", methods=["POST"])
def save_file():
    """حفظ ملف في المشروع"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "بيانات الملف مطلوبة"}), 400
        
        file_path = data.get("path")
        content = data.get("content", "")
        
        if not file_path:
            return jsonify({"error": "مسار الملف مطلوب"}), 400
        
        success, error = write_project_file(file_path, content)
        
        if not success:
            return jsonify({"error": error}), 400
        
        return jsonify({"message": f"تم حفظ الملف: {file_path}", "path": file_path})
    
    except Exception as e:
        return jsonify({"error": f"خطأ في حفظ الملف: {str(e)}"}), 500

@app.route("/execute", methods=["POST"])
def execute():
    """تنفيذ أمر في النظام"""
    try:
        data = request.json
        if not data or not data.get("command"):
            return jsonify({"error": "الأمر مطلوب"}), 400
        
        command = data.get("command")
        result = execute_command(command)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": f"خطأ في تنفيذ الأمر: {str(e)}"}), 500

@app.route("/health")
def health():
    """فحص حالة الخادم"""
    return jsonify({
        "status": "OK",
        "service": "Programming Assistant AI",
        "model": "llama-3.1-8b-instant",
        "features": ["chat", "code_analysis", "project_help"]
    })

if __name__ == "__main__":
    print("🚀 بدء تشغيل خادم Groq AI Agent")
    print("📍 الخادم متاح على: http://localhost:8000")
    print("💬 صفحة الدردشة: http://localhost:8000")
    print("🔗 API endpoint: http://localhost:8000/ask")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=8000)