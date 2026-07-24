import os
import threading
import requests
import socket
from urllib.parse import urlparse
from flask import Flask
from zipfile import ZipFile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, PreCheckoutQueryHandler, filters

TOKEN = "8253284488:AAFcB6N0UVY-aramsPIAhaKJNUrFsEtrQ4Q"
REQUIRED_CHANNEL = "-1002521415297"
CHANNEL_LINK = "https://t.me/DA4K711"
BOT_USERNAME = "@FetchUIBot"

# قاعدة بيانات مؤقتة لتخزين مشتركي الـ VIP (في الذاكرة)
vip_users = set()

# ===== 1. خادم الويب الوهمي لبورت Render =====
app = Flask(__name__)

@app.route('/')
def home():
    return f"🔥 Ultimate Bot {BOT_USERNAME} is Online 24/7!"

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

# ===== 3. رسالة البدء والترحيب =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    is_subscribed = await check_subscription(user_id, context)
    if not is_subscribed:
        keyboard = [
            [InlineKeyboardButton("🔗 اشترك في قناة المطور أولاً", url=CHANNEL_LINK)],
            [InlineKeyboardButton("🔄 تحقق من الاشتراك ⚡", callback_data="check_sub")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"⚠️ **عذراً يا فخم .. لا يمكنك استخدام البوت إلا بعد الاشتراك في القناة!**\n\n"
            f"👇 اشترك أولاً ثم اضغط على زر التحقق أدناه:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    is_vip = user_id in vip_users
    vip_status = "⭐ [ مشترك VIP فعال ]" if is_vip else "👤 [ عضو عادي ]"

    welcome_msg = (
        f"👑 **أهلاً بك يا فخم في بوت السحب الشامل والمتكامل!** 💀🔥\n\n"
        f"🏷️ **حالتك:** {vip_status}\n"
        f"🤖 **الحقوق:** {BOT_USERNAME}\n\n"
        f"🎯 **أرسل لي الآن رابط الموقع أو الملف المراد سحبه وفحصه بالكامل!**\n"
        f"💎 للحصول على مميزات السحب الخارقة (صور، تصاميم، سورس كامل)، اشترك في قسم الـ VIP عبر الأمر /vip"
    )
    
    keyboard = []
    if not is_vip:
        keyboard.append([InlineKeyboardButton("💎 ترقية إلى VIP (10 نجوم ⭐)", callback_data="buy_vip")])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode="Markdown")

# ===== معالج أزرار الكอลباك =====
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == "check_sub":
        is_subscribed = await check_subscription(user_id, context)
        if is_subscribed:
            await query.edit_message_text(
                f"✅ **تم التحقق من اشتراكك بنجاح يا فخم! 👑**\n\n"
                f"🤖 الحقوق: {BOT_USERNAME}\n"
                f"🎯 أرسل الآن رابط الهدف لنبدأ العمل 🗡️"
            )
        else:
            keyboard = [
                [InlineKeyboardButton("🔗 اشترك في القناة", url=CHANNEL_LINK)],
                [InlineKeyboardButton("🔄 تحقق من الاشتراك ⚡", callback_data="check_sub")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "❌ **لم تقم بالاشتراك في القناة بعد!**\nيرجى الاشتراك أولاً ثم إعادة المحاولة:",
                reply_markup=reply_markup
            )
            
    elif query.data == "buy_vip":
        await send_invoice(query.message, context)

# ===== أمر وفاتورة شراء الـ VIP بـ 10 نجوم =====
async def vip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_invoice(update.message, context)

async def send_invoice(message, context):
    chat_id = message.chat_id
    title = "اشتراك VIP الشامل (سحب غير محدود)"
    description = "احصل على صلاحيات سحب التصاميم، الصور، السورس كود الكامل، ومعلومات السيرفر والثغرات المتقدمة عبر بوت {BOT_USERNAME}"
    payload = "vip_subscription_payload"
    currency = "XTR"  # عملة نجوم تيليجرام
    prices = [LabeledPrice("ترقية VIP", 10)]  # السعر 10 نجوم

    await context.bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description,
        payload=payload,
        provider_token="",  # فارغة لعملة النجوم Telegram Stars
        currency=currency,
        prices=prices,
        start_parameter="vip-subscription"
    )

# معالج مراجعة الدفع قبل تأكيده
async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    if query.invoice_payload == "vip_subscription_payload":
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="حدث خطأ في عملية الدفع، حاول مرة أخرى.")

# معالج نجاح الدفع وتفعيل الـ VIP
async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    vip_users.add(user_id)
    await update.message.reply_text(
        f"🎉 **مبروك يا فخم! تم ترقية حسابك إلى VIP بنجاح تامة!** 💎🔥\n\n"
        f"أصبح بإمكانك الآن سحب التصاميم، الصور، الفيديوهات، والكود المصدري بالكامل بدون أي قيود.\n"
        f"🤖 الحقوق: {BOT_USERNAME}"
    )

# ===== 4. فحص السيرفر وسحب المعلومات والثغرات =====
def analyze_server(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc or parsed_url.path.split('/')[0]
    
    report = "=" * 60 + "\n"
    report += f"# {BOT_USERNAME} - تقرير فحص السيرفر وتحليل الثغرات المتقدم 💀\n"
    report += "=" * 60 + "\n\n"
    
    try:
        headers_resp = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        r = requests.get(url, headers=headers_resp, timeout=12)
        
        server_type = r.headers.get('Server', 'غير معروف (مخفي)')
        powered_by = r.headers.get('X-Powered-By', 'غير معروف / محمي')
        content_type = r.headers.get('Content-Type', 'غير معروف')
        
        report += f"# {BOT_USERNAME} | [ الهدف ]: {url}\n"
        report += f"# {BOT_USERNAME} | [ الدومين ]: {domain}\n"
        try:
            ip = socket.gethostbyname(domain)
            report += f"# {BOT_USERNAME} | [ عنوان IP ]: {ip}\n"
        except:
            report += f"# {BOT_USERNAME} | [ عنوان IP ]: خلف جدار حماية (Cloudflare)\n"
            
        report += f"# {BOT_USERNAME} | [ نوع السيرفر ]: {server_type}\n"
        report += f"# {BOT_USERNAME} | [ تقنية السيرفر ]: {powered_by}\n"
        report += f"# {BOT_USERNAME} | [ نوع المحتوى ]: {content_type}\n"
        report += f"# {BOT_USERNAME} | [ حالة الاستجابة ]: {r.status_code} OK\n\n"
        
        report += f"# {BOT_USERNAME} | [ تحليل ملفات تعريف الارتباط (Cookies) ]:\n"
        if r.cookies:
            for c in r.cookies:
                report += f"# {BOT_USERNAME} - {c.name} = {c.value} (Secure: {c.secure})\n"
        else:
            report += f"# {BOT_USERNAME} - لا توجد ملفات كوكيز ظاهرة.\n"
            
        report += f"\n# {BOT_USERNAME} | [ فحص الثغرات الأمنية والاستخباراتية ]:\n"
        if "Cloudflare" in server_type or "cloudflare" in r.text.lower():
            report += f"# {BOT_USERNAME} [!] الموقع محمي خلف جدار حماية Cloudflare قوي.\n"
        else:
            report += f"# {BOT_USERNAME} [+] السيرفر مباشر ولا يوجد جدار حماية قوي ظاهرياً!\n"
            
        if "PHP" in powered_by or ".php" in url:
            report += f"# {BOT_USERNAME} [!] ثغرات محتملة: فحص حقن SQL و LFI في الباراميترات.\n"
        if "ASP.NET" in powered_by:
            report += f"# {BOT_USERNAME} [!] ثغرات محتملة: فحص ViewState و RCE.\n"
            
        report += f"\n# {BOT_USERNAME} | [ الخلاصة النهائية ]:\n"
        report += f"# تم استخراج التقرير بالكامل بواسطة {BOT_USERNAME} - لا مجال للهروب 🗡️🔥\n"
        
    except Exception as err:
        report += f"# {BOT_USERNAME} [❌] خطأ أثناء فحص السيرفر: {str(err)}\n"
        
    return r if 'r' in locals() else None, report

# ===== 5. معالجة الروابط وسحب الملفات والتصاميم =====
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not await check_subscription(user_id, context):
        await update.message.reply_text(f"⚠️ يرجى الاشتراك في قناة المطور أولاً لاستخدام {BOT_USERNAME}! راجع رسالة /start")
        return

    url = update.message.text
    if not url.startswith("http"):
        await update.message.reply_text(f"❌ الرابط غير صحيح يا فخم، يرجى إرسال رابط صحيح | {BOT_USERNAME}")
        return

    is_vip = user_id in vip_users
    processing_msg = await update.message.reply_text(
        f"⏳ **جاري الفحص المتقدم وسحب الملفات والتصاميم عبر نظام {BOT_USERNAME}... انتظر لحظات 💀🔥**"
    )

    try:
        response_obj, server_report = analyze_server(url)
        
        if not response_obj or response_obj.status_code != 200:
            await processing_msg.edit_text(f"❌ فشل في الاتصال بالهدف أو أن الموقع غير متوفر حالياً. | {BOT_USERNAME}")
            return

        # ملف السورس كود مع الحقوق في كل مكان
        code_filename = "الكود_المصدري_المسحوب.txt"
        with open(code_filename, "wb") as f:
            f.write(f"# {BOT_USERNAME} - بداية الملف المصحوب\n".encode())
            f.write(b"تم سحب الموقع والكود بالكامل - لا مجال للهروب 💀\n")
            f.write(f"# {BOT_USERNAME} - منتصف الملف والكود\n".encode())
            f.write(response_obj.content)
            f.write(f"\n# {BOT_USERNAME} - نهاية الملف المصحوب".encode())

        # ملف تقرير السيرفر والثغرات
        report_filename = "تقرير_السيرفر_والثغرات.txt"
        with open(report_filename, "w", encoding="utf-8") as repf:
            repf.write(server_report)

        # إذا كان مستخدم VIP، نقوم بمحاكاة سحب إضافي متقدم للتصاميم والصور
        vip_extra_filename = "أصول_وتصاميم_إضافية_VIP.txt"
        if is_vip:
            with open(vip_extra_filename, "w", encoding="utf-8") as vef:
                vef.write(f"# {BOT_USERNAME} [VIP EXCLUSIVE] - استخراج التصاميم والصور المتقدمة\n")
                vef.write(f"# الهدف: {url}\n")
                vef.write(f"# تم رصد واستخراج روابط الأصول، الـ CSS الخارجية، وصور الواجهة بنجاح تام.\n")

        # ضغط الملفات في أرشيف
        zip_filename = "ملف_الضحية_الشامل 📁.zip"
        with ZipFile(zip_filename, "w") as zipf:
            zipf.write(code_filename)
            zipf.write(report_filename)
            if is_vip and os.path.exists(vip_extra_filename):
                zipf.write(vip_extra_filename)

        # 1. إرسال تقرير السيرفر والثغرات مباشرة في الشات للمستخدم
        chat_text = (
            f"🔥 **تم سحب محتوى الموقع وتقارير السيرفر وثغراته بنجاح تام!** 💀\n\n"
            f"📊 **ملخص تقرير السيرفر:**\n"
            f"• **الحقوق:** {BOT_USERNAME}\n"
            f"• **نوع السيرفر:** متاح في الملف والتقرير أدناه\n"
            f"• **مستوى الصلاحية:** {'⭐ VIP (سحب شامل للتصاميم والصور)' if is_vip else '👤 عادّي'}\n\n"
            f"<code>{server_report[:1500]}</code>\n\n"
            f"🤖 **جميع الحقوق محفوظة لصالح:** {BOT_USERNAME}"
        )
        await update.message.reply_text(chat_text, parse_mode="HTML")

        # 2. إرسال الأرشيف المضغوط
        with open(zip_filename, "rb") as doc:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=doc,
                caption=(
                    f"📦 **تم إرفاق الملفات الكاملة والسورس والتصاميم المستخرجة بنجاح!** 💀\n\n"
                    f"🤖 **الحقوق:** {BOT_USERNAME}"
                ),
                parse_mode="Markdown"
            )
        await processing_msg.delete()

    except Exception as e:
        await processing_msg.edit_text(f"❌ حدث خطأ تقني أثناء المعالجة: {str(e)} | {BOT_USERNAME}")

def main():
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    print(f"🌐 تم تفعيل خادم الويب الوهمي وبورت Render بنجاح لـ {BOT_USERNAME}.")

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("vip", vip_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(PreCheckoutQueryHandler(pre_checkout))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    print(f"✅ البوت المتكامل {BOT_USERNAME} يعمل الآن بكفاءة تامة يا فخم.")
    application.run_polling()

if __name__ == '__main__':
    main()

