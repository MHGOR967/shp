import os
import threading
import requests
import socket
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from flask import Flask
from zipfile import ZipFile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, PreCheckoutQueryHandler, filters

TOKEN = "8253284488:AAFcB6N0UVY-aramsPIAhaKJNUrFsEtrQ4Q"
REQUIRED_CHANNEL = "-1002521415297"
CHANNEL_LINK = "https://t.me/DA4K711"
BOT_USERNAME = "@FetchUIBot"

# ايدي الـ VIP المجاني الخاص بك يا فخم
vip_users = {8349168441}

# ===== 1. خادم الويب الوهمي للبورت =====
app = Flask(__name__)

@app.route('/')
def home():
    return f"Smart Crawler System Online - {BOT_USERNAME}"

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

# ===== 3. واجهة الترحيب =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    is_subscribed = await check_subscription(user_id, context)
    if not is_subscribed:
        keyboard = [
            [InlineKeyboardButton("اشترك في القناة الرسمية", url=CHANNEL_LINK)],
            [InlineKeyboardButton("تحقق من الاشتراك", callback_data="check_sub")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"أهلاً بك يا فخم. يرجى الاشتراك في قناة النظام أولاً للمتابعة.\n\n"
            f"بعد إتمام الاشتراك، اضغط على زر التحقق أدناه:",
            reply_markup=reply_markup
        )
        return

    is_vip = user_id in vip_users
    vip_status = "VIP (صلاحيات الزحف والسحب الكامل)" * is_vip or "عضو أساسي"

    welcome_msg = (
        f"مرحباً بك في نظام السحب والتحليل الذكي.\n\n"
        f"• مستوى الحساب: {vip_status}\n"
        f"• الخدمة: {BOT_USERNAME}\n\n"
        f"أرسل رابط الهدف (URL) وسيقوم النظام بتحليله بالكامل."
    )
    
    keyboard = []
    if not is_vip:
        keyboard.append([InlineKeyboardButton("ترقية الحساب إلى VIP (10 نجوم)", callback_data="buy_vip")])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == "check_sub":
        is_subscribed = await check_subscription(user_id, context)
        if is_subscribed:
            await query.edit_message_text(
                f"تم التحقق بنجاح.\n\n"
                f"أرسل رابط الهدف الآن لنبدأ عمليات الاستخراج."
            )
        else:
            keyboard = [
                [InlineKeyboardButton("اشترك في القناة", url=CHANNEL_LINK)],
                [InlineKeyboardButton("تحقق من الاشتراك", callback_data="check_sub")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "لم يتم رصد اشتراكك. يرجى الانضمام للقناة ثم المحاولة مرة أخرى:",
                reply_markup=reply_markup
            )
            
    elif query.data == "buy_vip":
        await send_invoice(query.message, context)

async def vip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_invoice(update.message, context)

async def send_invoice(message, context):
    chat_id = message.chat_id
    title = "اشتراك VIP الشامل (الزحف المتقدم)"
    description = "صلاحيات سحب وتحليل كافة الأصول، الصور، والسكربتات الخارجية للمواقع المستهدفة."
    payload = "vip_subscription_payload"
    currency = "XTR"
    prices = [LabeledPrice("VIP Access", 10)]

    await context.bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description,
        payload=payload,
        provider_token="",
        currency=currency,
        prices=prices,
        start_parameter="vip-subscription"
    )

async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    if query.invoice_payload == "vip_subscription_payload":
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="فشلت عملية الدفع.")

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    vip_users.add(user_id)
    await update.message.reply_text("تم تفعيل اشتراك VIP بنجاح. استمتع بكافة صلاحيات السحب والاستخراج المطلقة.")

# ===== 4. فحص السيرفر وتحليل البنية =====
def analyze_server(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc or parsed_url.path.split('/')[0]
    
    report = "============================================================\n"
    report += f"  تقرير تحليل البنية التقنية والسيرفر المستهدف\n"
    report += "============================================================\n\n"
    
    try:
        headers_resp = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        r = requests.get(url, headers=headers_resp, timeout=12)
        
        server_type = r.headers.get('Server', 'مخفي / غير مسجل')
        powered_by = r.headers.get('X-Powered-By', 'غير معلن')
        content_type = r.headers.get('Content-Type', 'غير معروف')
        
        report += f"[•] الهدف الأساسي : {url}\n"
        report += f"[•] النطاق (Domain) : {domain}\n"
        try:
            ip = socket.gethostbyname(domain)
            report += f"[•] عنوان الخادم (IP) : {ip}\n"
        except:
            report += f"[•] عنوان الخادم (IP) : محمى خلف جدار حماية (Cloudflare)\n"
            
        report += f"[•] نوع السيرفر : {server_type}\n"
        report += f"[•] التقنية المشغلة : {powered_by}\n"
        report += f"[•] نوع البيانات : {content_type}\n"
        report += f"[•] كود الاستجابة : {r.status_code} OK\n\n"
        
        report += "ملاحظات الفحص والاستخبارات:\n"
        report += f"تمت معالجة الطلب بواسطة {BOT_USERNAME}.\n"
        
    except Exception as err:
        report += f"[خطأ] تعذر إتمام التحليل: {str(err)}\n"
        
    return r if 'r' in locals() else None, report

# ===== 5. محرك الزحف الذكي للـ VIP (سحب الصور والستايلات والسكربتات) =====
def smart_crawler(url, html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    assets = {
        "images": set(),
        "stylesheets": set(),
        "scripts": set()
    }
    
    # استخراج الصور
    for img in soup.find_all('img'):
        src = img.get('src') or img.get('data-src')
        if src:
            assets["images"].add(urljoin(url, src))
            
    # استخراج ملفات الستايل CSS
    for link in soup.find_all('link'):
        if 'stylesheet' in link.get('rel', []):
            href = link.get('href')
            if href:
                assets["stylesheets"].add(urljoin(url, href))
                
    # استخراج السكربتات JS الخارجية
    for script in soup.find_all('script'):
        src = script.get('src')
        if src:
            assets["scripts"].add(urljoin(url, src))
            
    return assets

# ===== 6. معالجة الروابط وتنفيذ الجرف =====
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not await check_subscription(user_id, context):
        await update.message.reply_text(f"يرجى الاشتراك في القناة أولاً لاستخدام {BOT_USERNAME}.")
        return

    url = update.message.text
    if not url.startswith("http"):
        await update.message.reply_text("الرابط المدخل غير صحيح. يرجى إرسال رابط صالح.")
        return

    is_vip = user_id in vip_users
    processing_msg = await update.message.reply_text("جاري فحص الصفحة، تحليل الكود، والبدء في استخراج الأصول...")

    try:
        response_obj, server_report = analyze_server(url)
        
        if not response_obj or response_obj.status_code != 200:
            await processing_msg.edit_text("تعذر الاتصال بالهدف أو أن الصفحة غير متاحة.")
            return

        # حفظ الكود المصدري الأساسي
        code_filename = "source_code.txt"
        with open(code_filename, "wb") as f:
            f.write(f"# Processed by {BOT_USERNAME}\n".encode('utf-8'))
            f.write(response_obj.content)

        report_filename = "server_report.txt"
        with open(report_filename, "w", encoding="utf-8") as repf:
            repf.write(server_report)

        # ملف لتخزين روابط الأصول المستخرجة العادية
        assets_filename = "extracted_assets_list.txt"
        
        # إذا كان مستخدم VIP، نقوم بالزحف الذكي واستخراج كافة الروابط والملفات الخارجية
        if is_vip:
            crawled_data = smart_crawler(url, response_obj.text)
            with open(assets_filename, "w", encoding="utf-8") as af:
                af.write(f"=== VIP SMART CRAWLER MANIFEST - {BOT_USERNAME} ===\n")
                af.write(f"Target URL: {url}\n\n")
                
                af.write(f"[+] Images Found ({len(crawled_data['images'])}):\n")
                for img_url in crawled_data['images']:
                    af.write(f"  - {img_url}\n")
                    
                af.write(f"\n[+] Stylesheets Found ({len(crawled_data['stylesheets'])}):\n")
                for css_url in crawled_data['stylesheets']:
                    af.write(f"  - {css_url}\n")
                    
                af.write(f"\n[+] Scripts Found ({len(crawled_data['scripts'])}):\n")
                for js_url in crawled_data['scripts']:
                    af.write(f"  - {js_url}\n")
        else:
            with open(assets_filename, "w", encoding="utf-8") as af:
                af.write("ترقية الحساب إلى VIP مطلوبة لاستخدام محرك الزحف الذكي واستخراج الأصول والتصاميم بالكامل.\n")

        zip_filename = "extracted_package.zip"
        with ZipFile(zip_filename, "w") as zipf:
            zipf.write(code_filename)
            zipf.write(report_filename)
            if os.path.exists(assets_filename):
                zipf.write(assets_filename)

        # إرسال تقرير موجز في الشات
        chat_text = (
            f"تمت عملية التحليل واستخراج الأصول بنجاح.\n\n"
            f"• الصلاحية: {'⭐ VIP (محرك زحف نشط)' if is_vip else '👤 أساسي'}\n"
            f"• النظام: {BOT_USERNAME}\n\n"
            f"<pre>{server_report[:800]}</pre>"
        )
        await update.message.reply_text(chat_text, parse_mode="HTML")

        with open(zip_filename, "rb") as doc:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=doc,
                caption=f"ملف الأرشيف الكامل متضمن السورس والأصول جاهز.\nالخدمة: {BOT_USERNAME}"
            )
        await processing_msg.delete()

    except Exception as e:
        await processing_msg.edit_text(f"حدث خطأ أثناء تنفيذ عملية الاستخراج: {str(e)}")

def main():
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("vip", vip_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(PreCheckoutQueryHandler(pre_checkout))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    application.run_polling()

if __name__ == '__main__':
    main()
