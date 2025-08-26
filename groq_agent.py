import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS   # ⬅️ يسمح بالاتصال من المتصفح
from groq import Groq

# تحميل متغيرات البيئة
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("❌ لم يتم العثور على GROQ_API_KEY في ملف .env")

# إنشاء عميل Groq
client = Groq(api_key=api_key)

# تطبيق Flask
app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)  # ⬅️ تفعيل CORS

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_message = data.get("message", "")

    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[{"role": "user", "content": user_message}],
    )

    return jsonify({"reply": response.choices[0].message.content})

@app.route("/")
def home():
    return app.send_static_file("index.html")

if __name__ == "__main__":
    app.run(debug=True)
