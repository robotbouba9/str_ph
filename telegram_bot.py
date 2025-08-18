import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from database import db, Product, Category

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, continue without it

# Get bot token from environment variable
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Initialize Flask app for database context
app = Flask(__name__)
# Use absolute path for database
import os
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'phone_store.db')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = """
🔥 *مرحباً بك في بوت متجر الهواتف!* 📱

🛍️ يمكنك البحث عن المنتجات بسهولة عن طريق:
• كتابة اسم المنتج
• كتابة اسم الماركة (مثل: Apple, Samsung)
• كتابة الموديل (مثل: iPhone 15, Galaxy S24)
• كتابة أي كلمة من وصف المنتج

📝 *أمثلة للبحث:*
• iPhone
• سماعات
• شاحن سريع
• كابل

💡 اكتب /help للحصول على المساعدة
    """
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_message = """
📋 *كيفية استخدام البوت:*

🔍 *للبحث عن المنتجات:*
فقط اكتب أي كلمة أو عبارة تريد البحث عنها

📱 *أمثلة للبحث:*
• `iPhone` - للبحث عن هواتف آيفون
• `Samsung` - للبحث عن منتجات سامسونج
• `سماعات` - للبحث عن السماعات
• `شاحن` - للبحث عن الشواحن
• `كابل` - للبحث عن الكابلات

ℹ️ *معلومات المنتج تشمل:*
• الاسم والماركة والموديل
• السعر والكمية المتوفرة
• اللون والوصف

🆘 اكتب /start للعودة للرسالة الترحيبية
    """
    await update.message.reply_text(help_message, parse_mode="Markdown")

async def search_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.message.text
    try:
        results = []
        with app.app_context():
            # Search for products by name, brand, model, or description
            products = Product.query.filter(
                (Product.name.ilike(f'%{query}%')) |
                (Product.brand.ilike(f'%{query}%')) |
                (Product.model.ilike(f'%{query}%')) |
                (Product.description.ilike(f'%{query}%'))
            ).limit(10).all()  # Limit results to 10

            if products:
                for product in products:
                    # Format product info
                    product_info = f"*{product.name}* ({product.brand} {product.model})\n"
                    product_info += f"💰 السعر: {product.price_sell} جنيه\n"
                    product_info += f"📦 الكمية المتوفرة: {product.quantity}\n"
                    if product.color:
                        product_info += f"🎨 اللون: {product.color}\n"
                    if product.description:
                        desc = product.description[:100] + "..." if len(product.description) > 100 else product.description
                        product_info += f"📝 الوصف: {desc}"
                    results.append(product_info)
                
                response_text = "🔍 *المنتجات المطابقة:*\n\n" + "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n".join(results)
            else:
                response_text = "❌ عذراً، لم يتم العثور على منتجات مطابقة لاستعلامك.\n\n💡 جرب البحث باستخدام:\n• اسم المنتج\n• الماركة\n• الموديل\n• كلمات من الوصف"

        await update.message.reply_text(response_text, parse_mode="Markdown")
    except Exception as e:
        error_message = "❌ حدث خطأ أثناء البحث. يرجى المحاولة مرة أخرى."
        await update.message.reply_text(error_message)

def main() -> None:
    if not TOKEN:
        print("❌ خطأ: لم يتم تعيين رمز البوت (TELEGRAM_BOT_TOKEN)")
        print("يرجى تعيين متغير البيئة TELEGRAM_BOT_TOKEN أو تعديل الكود")
        return

    try:
        # Initialize database tables
        with app.app_context():
            db.create_all()
            print("✅ تم تهيئة قاعدة البيانات بنجاح")

        # Create application
        application = Application.builder().token(TOKEN).build()

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_products))

        print("🤖 تم تشغيل بوت التليجرام بنجاح!")
        print("📱 البوت جاهز لاستقبال الرسائل...")
        print("⏹️ اضغط Ctrl+C لإيقاف البوت")
        
        # Start polling
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {str(e)}")
        print("تأكد من:")
        print("1. صحة رمز البوت (TOKEN)")
        print("2. الاتصال بالإنترنت")
        print("3. تثبيت المتطلبات: pip install python-telegram-bot")

if __name__ == '__main__':
    main()
