import os
import threading
import requests
import socket
from urllib.parse import urlparse
from flask import Flask
from zipfile import ZipFile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

TOKEN = "8253284488:AAFcB6N0UVY-aramsPIAhaKJNUrFsEtrQ4Q"
REQUIRED_CHANNEL = "-1002521415297"
CHANNEL_LINK = "https://t.me/DA4K711"

# ===== 1. خادم الويب الوهمي لبورت Render =====
app = Flask(__name__)

@app.route('/')
def home():
    return "🔥 FokhM.com Pro Bot is Online 24/7!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ===== 2. التحقق من الاشتراك الإجباري =====
async def check_subscription(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception:
        pass
    return False

# ===== 3. رسالة البدء والترحيب المرعبة =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # فحص الاشتراك الإجباري
    is_subscribed = await check_subscription(user_id, context)
    if not is_subscribed:
        keyboard = [
            [InlineKeyboardButton("🔗 اضغط هنا للاشتراك في القناة", url=CHANNEL_LINK)],
            [InlineKeyboardButton("🔄 تحقق من الاشتراك ⚡", callback_data="check_sub")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"⚠️ **عذراً يا {user.first_name} .. لا يمكنك استخدام البوت إلا بعد الاشتراك في قناة المطور!**\n\n"
            f"👇 اشترك أولاً ثم اضغط على زر التحقق أدناه:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    welcome_msg = (
        f"👑 **أهلاً بك يا فخم في بوت السحب والاختراق الاحترافي!** 💀🔥\n\n"
        f"⚡ **المطور:** @KHAIN3\n"
        f"🌐 **منصة الموقع:** fokhm.com\n\n"
        f"🎯 **أرسل لي الآن رابط الموقع أو الملف المراد سحبه وفحص سيرفراته بالكامل!**"
    )
    await update.message.reply_text(welcome_msg, parse_mode="Markdown")

# ===== معالج زر التحقق من الاشتراك =====
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == "check_sub":
        is_subscribed = await check_subscription(user_id, context)
        if is_subscribed:
            await query.edit_message_text(
                "✅ **تم التحقق من اشتراكك بنجاح يا فخم! 👑**\n\n"
                "🎯 أرسل الآن رابط الهدف لنبدأ العمل وتدمير السيرفرات 🗡️"
            )
        else:
            keyboard = [
                [InlineKeyboardButton("🔗 اضغط هنا للاشتراك في القناة", url=CHANNEL_LINK)],
                [InlineKeyboardButton("🔄 تحقق من الاشتراك ⚡", callback_data="check_sub")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "❌ **لم تقم بالاشتراك في القناة بعد!**\nيرجى الاشتراك أولاً ثم إعادة المحاولة:",
                reply_markup=reply_markup
            )

# ===== 4. فحص السيرفر وسحب المعلومات والثغرات =====
def analyze_server(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc or parsed_url.path.split('/')[0]
    
    report = "=" * 50 + "\n"
    report += "💀 تقرير فحص السيرفر وتحليل الثغرات المتقدم - بواسطة وهـم 💀\n"
    report += "=" * 50 + "\n\n"
    
    try:
        # جلب الهيدرز ومعلومات الموقع
        headers_resp = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        r = requests.get(url, headers=headers_resp, timeout=10)
        
        server_type = r.headers.get('Server', 'غير معروف (مخفي)')
        powered_by = r.headers.get('X-Powered-By', 'غير معروف / محمي')
        content_type = r.headers.get('Content-Type', 'غير معروف')
        
        report += f"🌐 [ الهدف ]: {url}\n"
        report += f"🌍 [ الدومين ]: {domain}\n"
        try:
            ip = socket.gethostbyname(domain)
            report += f"📍 [ عنوان IP ]: {ip}\n"
        except:
            report += f"📍 [ عنوان IP ]: يتعذر الحل ( خلف حماية Cloudflare )\n"
            
        report += f"🖥️ [ نوع السيرفر ]: {server_type}\n"
        report += f"⚙️ [ لغة/تقنية السيرفر (X-Powered-By) ]: {powered_by}\n"
        report += f"📦 [ نوع المحتوى ]: {content_type}\n"
        report += f"📊 [ حالة الاستجابة ]: {r.status_code} OK\n\n"
        
        report += "🍪 [ تحليل ملفات تعريف الارتباط (Cookies) ]:\n"
        if r.cookies:
            for c in r.cookies:
                report += f" - {c.name} = {c.value} (Secure: {c.secure})\n"
        else:
            report += " - لا توجد ملفات كوكيز ظاهرة.\n"
            
        report += "\n🛡️ [ فحص الثغرات الأمنية المحتملة والاستخباراتية ]:\n"
        # فحص وجود حماية أو ثغرات رئيسية استنادا للبيانات
        if "Cloudflare" in server_type or "cloudflare" in r.text.lower():
            report += " [!] الموقع محمي خلف جدار حماية Cloudflare (يحتاج لفحص الـ Subdomains).\n"
        else:
            report += " [+] السيرفر مباشر ولا يوجد جدار حماية قوي ظاهرياً!\n"
            
        if "PHP" in powered_by or ".php" in url:
            report += " [!] تقنية PHP مكتشفة: احذر من ثغرات LFI/RFI و SQL Injection في الباراميترات.\n"
        if "ASP.NET" in powered_by:
            report += " [!] تقنية ASP.NET مكتشفة: ابحث عن ثغرات ViewState و Remote Code Execution.\n"
            
        report += "\n🔍 [ استنتاج المطور وهـم ]:\n"
        report += "تم رصد الهدف بنجاح، استخرجنا الكود المصدري ومعلومات الهيدرز بالكامل. لا مجال للهروب 🗡️🔥\n"
        
    except Exception as err:
        report += f"❌ حدث خطأ أثناء فحص السيرفر: {str(err)}\n"
        
    return r if 'r' in locals() else None, report

# ===== 5. معالجة روابط الضحايا والسيرفرات =====
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # فحص الاشتراك الإجباري أولاً
    if not await check_subscription(user_id, context):
        await update.message.reply_text("⚠️ يرجى الاشتراك في قناة المطور أولاً لاستخدام البوت! راجع رسالة /start")
        return

    url = update.message.text
    if not url.startswith("http"):
        await update.message.reply_text("❌ الرابط غير صحيح يا فخم، يرجى إرسال رابط يبدأ بـ http أو https")
        return

    processing_msg = await update.message.reply_text("⏳ جاري سحب كود الموقع وفحص سيرفرات الضحية واستخراج الثغرات... انتظر لحظات 💀🔥")

    try:
        # جلب محتوى الموقع وتحليل السيرفر
        response_obj, server_report = analyze_server(url)
        
        if not response_obj or response_obj.status_code != 200:
            await processing_msg.edit_text("❌ فشل في الاتصال بالهدف أو أن الموقع غير متوفر حالياً.")
            return

        # حفظ الملف المستهدف (الكود المصدري)
        code_filename = "المسحوب_الهدف.txt"
        with open(code_filename, "wb") as f:
            header_watermark = "تم سحب الموقع والكود بواسطة المطور وهـم لامجال للهروب 💀\n"
            poetry = "ما تهرب إلا الجبناء .. والمطور يقطع كل عنق 🗡️🔥\n\n"
            f.write(header_watermark.encode())
            f.write(poetry.encode())
            f.write(response_obj.content)

        # حفظ تقرير السيرفر والثغرات المفصل
        report_filename = "تقرير_فحص_السيرفر_والثغرات.txt"
        with open(report_filename, "w", encoding="utf-8") as repf:
            repf.write(server_report)

        # ضغط الملفات في أرشيف مضغوط
        zip_filename = "ملف_الضحية_الشامل 📁.zip"
        with ZipFile(zip_filename, "w") as zipf:
            zipf.write(code_filename)
            zipf.write(report_filename)

        # إرسال الملف المضغوط للعميل
        with open(zip_filename, "rb") as doc:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=doc,
                caption=(
                    "🔥 **تم سحب محتوى الموقع وتقارير السيرفر وثغراته بنجاح تام!** 💀\n\n"
                    "👑 **صطور المطور:** @KHAIN3\n"
                    "🌐 **موقعك:** fokhm.com"
                ),
                parse_mode="Markdown"
            )
        await processing_msg.delete()

    except Exception as e:
        await processing_msg.edit_text(f"❌ حدث خطأ تقني أثناء المعالجة: {str(e)}")

def main():
    # تشغيل خادم الويب الوهمي للبورت
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    print("🌐 تم تفعيل خادم الويب الوهمي وبورت Render بنجاح.")

    # تشغيل بوت التيليجرام
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    print("✅ البوت الاحترافي يعمل الآن بكفاءة تامة يا فخم.")
    application.run_polling()

if __name__ == '__main__':
    main()

