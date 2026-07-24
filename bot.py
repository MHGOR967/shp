import os
import threading
import requests
from flask import Flask
from zipfile import ZipFile
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

TOKEN = "8253284488:AAFcB6N0UVY-aramsPIAhaKJNUrFsEtrQ4Q"

# ===== 1. إنشاء خادم ويب وهمي للتعامل مع بورت Render =====
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot is running successfully, FokhM.com!"

def run_web_server():
    # Render يزودنا برقم البورت تلقائياً عبر متغير البيئة PORT، وإذا لم يوجد نستخدم 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


# ===== 2. دوام وأوامر بوت التيليجرام =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text="أهلاً بك يا فخم 👑.. أرسل الآن رابط الملف 🎯")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    url = update.message.text

    if not url or not url.startswith("http"):
        await context.bot.send_message(chat_id=chat_id, text="❌ الرابط غير صحيح")
        return

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            await context.bot.send_message(chat_id=chat_id, text="❌ فشل في تحميل الملف")
            return

        filename = "المسحوب.js"
        with open(filename, "wb") as f:
            header = "تم سحب الملف بواسطة المطور وهـم لامجال للهروب 💀\n"
            poetry = "ما تهرب إلا الجبناء .. والمطور يقطع كل عنق 🗡️🔥\n\n"
            f.write(header.encode())
            f.write(poetry.encode())
            f.write(r.content)

        with open("ملف مهم.txt", "w", encoding="utf-8") as impf:
            impf.write("🔥 طناخه وتكبر اني سحبته")

        zip_filename = "بح بح 🖐😂.zip"
        with ZipFile(zip_filename, "w") as zipf:
            zipf.write(filename)
            zipf.write("ملف مهم.txt")

        with open(zip_filename, "rb") as doc:
            await context.bot.send_document(
                chat_id=chat_id,
                document=doc,
                caption="📦 تم السحب بنجاح بواسطة @KHAIN3"
            )

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ خطأ أثناء المعالجة: {e}")

def main():
    # تشغيل خادم الويب الوهمي في خيط (Thread) منفصل لكي لا يعطل البوت
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    print("🌐 تم تفعيل خادم الويب الوهمي واستجابة البورت بنجاح.")

    # تشغيل البوت بالطريقة الحديثة
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    print("✅ البوت يعمل الآن على Render بكفاءة تامة يا فخم.")
    application.run_polling()

if __name__ == '__main__':
    main()

