import telebot
import requests
from datetime import datetime
from telebot import types

BOT_TOKEN = "8481866188:AAHq1aHpze1zOkqw4uypl8pb0-Bcp0nAmD4"
AIRTABLE_TOKEN = "patnOmcrxm6o9KT2T.185f28d0b1d8e0ce28671be2edc7e441f7a5aecf0b01c01458c730693a388b21"
AIRTABLE_BASE = "appvuIfgZfQAxPsld"
AIRTABLE_TABLE = "tblkFGjUvXvIrjhcE"
PASSWORD = "123$"

bot = telebot.TeleBot(BOT_TOKEN)
authorized_users = set()

def add_to_airtable(coin, chat_id):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE}/{AIRTABLE_TABLE}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "records": [{
            "fields": {
                "coin": coin,
                "chat_id": chat_id,
                "timestamp": datetime.now().isoformat(),
                "status": "pending"
            }
        }]
    }
    requests.post(url, headers=headers, json=data)

def show_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📊 تحليل يومي"))
    markup.add(types.KeyboardButton("🔍 تحليل عملة"))
    bot.send_message(chat_id, "✅ اختر:", reply_markup=markup)

def is_valid_coin(text):
    # تجاهل الردود على السؤال
    ignore = ["نعم", "لا", "✅", "❌", "yes", "no", "رجوع", "🔙"]
    if text.lower() in [i.lower() for i in ignore]:
        return False
    # رمز العملة: حروف فقط، 2-10 أحرف
    clean = text.upper().replace("$", "").replace("/", "").replace("USDT", "")
    return clean.isalpha() and 2 <= len(clean) <= 10

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🔐 أدخل كلمة المرور:")

@bot.message_handler(func=lambda m: True)
def handle(message):
    chat_id = message.chat.id
    text = message.text.strip()
    
    # التحقق من الباسورد
    if chat_id not in authorized_users:
        if text == PASSWORD:
            authorized_users.add(chat_id)
            bot.send_message(chat_id, "✅ مرحباً!")
            show_menu(chat_id)
        else:
            bot.send_message(chat_id, "❌ خطأ. حاول مرة أخرى:")
        return
    
    # الردود على سؤال الدخول - تجاهلها
    if text.lower() in ["نعم", "لا", "✅", "❌", "yes", "no"]:
        if "نعم" in text or "✅" in text:
            bot.send_message(chat_id, "✅ تم! سأتابع الصفقة وأرسل لك التحديثات.")
        else:
            bot.send_message(chat_id, "👀 تم، للاطلاع فقط.")
        show_menu(chat_id)
        return
    
    # القائمة
    if "يومي" in text:
        bot.send_message(chat_id, "⏳ جاري طلب التحليل...")
        add_to_airtable("TOP10", chat_id)
        return
    
    if "عملة" in text:
        bot.send_message(chat_id, "🔍 أرسل رمز العملة:")
        return
    
    if text == "🔙 رجوع":
        show_menu(chat_id)
        return
    
    # التحقق من رمز العملة
    if is_valid_coin(text):
        coin = text.upper().replace("$", "").replace("USDT", "")
        bot.send_message(chat_id, f"⏳ جاري تحليل {coin}...")
        add_to_airtable(coin, chat_id)
    else:
        show_menu(chat_id)

print("Bot running...")
bot.infinity_polling()
