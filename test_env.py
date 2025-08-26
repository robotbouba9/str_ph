import os
from dotenv import load_dotenv

# تحميل ملف .env
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if api_key:
    print("✅ المفتاح موجود وتم قراءته بنجاح:")
    print(api_key)
else:
    print("❌ المفتاح غير موجود! تأكد من إنشاء ملف .env ووضع المفتاح بداخله.")
