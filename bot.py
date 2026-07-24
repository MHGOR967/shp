import os
import threading
import requests
import socket
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from flask import Flask
from zipfile import ZipFile, ZIP_DEFLATED
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
    return f"True Cloner Engine Online - {BOT_USERNAME}"

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
    vip_status = "VIP (استنساخ شامل للملفات والأصول)" * is_vip or "عضو أساسي"

    welcome_msg = (
        f"مرحباً بك في محرك النسخ والاستنساخ الشامل.\n\n"
        f"• مستوى الحساب: {vip_status}\n"
        f"• الخدمة: {BOT_USERNAME}\n\n"
        f"أرسل رابط الهدف (URL) وسيقوم النظام بسحب الموقع بجميع ملفاته وتصاميمه بمساراتها المتناسقة."
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
                f"أرسل رابط الهدف الآن لنبدأ الاستنساخ الكامل."
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
    title = "اشتراك VIP الشامل (الاستنساخ الفعلي)"
    description = "صلاحيات تحميل وسحب الصور، الستايلات، والسكربتات الحقيقية مع تعديل المسارات."
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
    await update.message.reply_text("تم تفعيل اشتراك VIP بنجاح. استمتع بمحرك الاستنساخ الكامل غير المحدود.")

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
        
        report += f"تمت معالجة الطلب بواسطة {BOT_USERNAME}.\n"
        
    except Exception as err:
        report += f"[خطأ] تعذر إتمام التحليل: {str(err)}\n"
        
    return r if 'r' in locals() else None, report

# ===== 5. محرك الاستنساخ الفعلي وتحميل الملفات وتعديل المسارات =====
def clone_website(base_url, html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    downloaded_assets = {} # مسار محلي -> محتوى بايتات
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    # 1. معالجة الصور
    for idx, img in enumerate(soup.find_all('img')):
        src = img.get('src') or img.get('data-src')
        if src:
            absolute_url = urljoin(base_url, src)
            ext = os.path.splitext(urlparse(absolute_url).path)[1] or '.png'
            local_path = f"assets/images/img_{idx}{ext}"
            try:
                img_data = requests.get(absolute_url, headers=headers, timeout=5).content
                downloaded_assets[local_path] = img_data
                img['src'] = local_path # تعديل المسار في HTML ليكون محلياً
                if img.get('data-src'):
                    img['data-src'] = local_path
            except:
                pass

    # 2. معالجة ملفات الـ CSS (الستايلات)
    for idx, link in enumerate(soup.find_all('link')):
        if 'stylesheet' in link.get('rel', []):
            href = link.get('href')
            if href:
                absolute_url = urljoin(base_url, href)
                local_path = f"assets/css/style_{idx}.css"
                try:
                    css_data = requests.get(absolute_url, headers=headers, timeout=5).content
                    downloaded_assets[local_path] = css_data
                    link['href'] = local_path
                except:
                    pass

    # 3. معالجة السكربتات JS الخارجية
    for idx, script in enumerate(soup.find_all('script')):
        src = script.get('src')
        if src:
            absolute_url = urljoin(base_url, src)
            local_path = f"assets/js/script_{idx}.js"
            try:
                js_data = requests.get(absolute_url, headers=headers, timeout=5).content
                downloaded_assets[local_path] = js_data
                script['src'] = local_path
            except:
                pass

    return str(soup), downloaded_assets

# ===== 6. معالجة الروابط وتغليف المشروع =====
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
    processing_msg = await update.message.reply_text("جاري استنساخ الموقع بالكامل، تحميل الصور والستايلات والسكربتات، وتنسيق المسارات...")

    try:
        response_obj, server_report = analyze_server(url)
        
        if not response_obj or response_obj.status_code != 200:
            await processing_msg.edit_text("تعذر الاتصال بالهدف أو أن الصفحة غير متاحة.")
            return

        report_filename = "server_report.txt"
        with open(report_filename, "w", encoding="utf-8") as repf:
            repf.write(server_report)

        zip_filename = "cloned_website_package.zip"
        
        # بناء الأرشيف المضغوط
        with ZipFile(zip_filename, "w", ZIP_DEFLATED) as zipf:
            zipf.write(report_filename)
            
            if is_vip:
                # تشغيل محرك الاستنساخ الشامل للـ VIP
                cloned_html, assets = clone_website(url, response_obj.text)
                
                # حفظ صفحة الـ HTML المعدلة
                html_filename = "index.html"
                with open(html_filename, "w", encoding="utf-8") as hf:
                    hf.write(f"<!-- Cloned & Processed by {BOT_USERNAME} -->\n")
                    hf.write(cloned_html)
                zipf.write(html_filename)
                
                # إضافة كافة الأصول المحملة بمساراتها المتناسقة داخل الأرشيف
                for path, data in assets.items():
                    zipf.writestr(path, data)
            else:
                # العضو العادي يسحب HTML فقط بدون جرف الأصول
                html_filename = "index.html"
                with open(html_filename, "wb") as hf:
                    hf.write(f"<!-- Basic version by {BOT_USERNAME} -->\n".encode('utf-8'))
                    hf.write(response_obj.content)
                zipf.write(html_filename)

        # تقرير الشات
        chat_text = (
            f"تم استنساخ الموقع وتجهيز حزمة النشر بنجاح.\n\n"
            f"• المستوى: {'⭐ VIP (استنساخ فعلي للملفات والمسارات)' if is_vip else '👤 أساسي (HTML فقط)'}\n"
            f"• النظام: {BOT_USERNAME}\n\n"
            f"الملف جاهز للرفع المباشر على أي استضافة (رفع وفك الضغط ويعمل فوراً)."
        )
        await update.message.reply_text(chat_text)

        with open(zip_filename, "rb") as doc:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=doc,
                caption=f"حزمة الموقع المستسخ متضمنة index.html ومجلدات assets بالمسارات الصحيحة.\nالخدمة: {BOT_USERNAME}"
            )
        await processing_msg.delete()

    except Exception as e:
        await processing_msg.edit_text(f"حدث خطأ أثناء عملية الاستنساخ: {str(e)}")

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
