import telebot
import requests
from datetime import datetime, timedelta
from telebot import types
import json
import os

BOT_TOKEN = "8481866188:AAHq1aHpze1zOkqw4uypl8pb0-Bcp0nAmD4"
AIRTABLE_TOKEN = "patnOmcrxm6o9KT2T.185f28d0b1d8e0ce28671be2edc7e441f7a5aecf0b01c01458c730693a388b21"
AIRTABLE_BASE = "appvuIfgZfQAxPsld"
AIRTABLE_TABLE = "tblkFGjUvXvIrjhcE"
PASSWORD = "123$"

bot = telebot.TeleBot(BOT_TOKEN)

# حفظ المستخدمين المصرح لهم مع تاريخ التصريح
auth_file = "authorized_users.json"

def load_authorized():
    try:
        if os.path.exists(auth_file):
            with open(auth_file, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_authorized(data):
    with open(auth_file, 'w') as f:
        json.dump(data, f)

def is_authorized(chat_id):
    data = load_authorized()
    chat_str = str(chat_id)
    if chat_str in data:
        auth_date = datetime.fromisoformat(data[chat_str])
        if datetime.now() - auth_date < timedelta(days=30):
            return True
    return False

def authorize_user(chat_id):
    data = load_authorized()
    data[str(chat_id)] = datetime.now().isoformat()
    save_authorized(data)

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
    bot.send_message(chat_id, "✅ مرحباً! اختر من القائمة:", reply_markup=markup)

waiting_password = set()

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if is_authorized(chat_id):
        show_menu(chat_id)
    else:
        waiting_password.add(chat_id)
        bot.send_message(chat_id, "🔐 مرحباً بك!\n\nأدخل كلمة المرور للمتابعة:")

@bot.message_handler(func=lambda m: True)
def handle(message):
    chat_id = message.chat.id
    text = message.text.strip()
    
    # انتظار الباسورد
    if chat_id in waiting_password:
        if text == PASSWORD:
            waiting_password.discard(chat_id)
            authorize_user(chat_id)
            bot.send_message(chat_id, "✅ تم التحقق بنجاح!")
            show_menu(chat_id)
        else:
            bot.send_message(chat_id, "❌ كلمة المرور خاطئة. حاول مرة أخرى:")
        return
    
    # التحقق من الصلاحية
    if not is_authorized(chat_id):
        waiting_password.add(chat_id)
        bot.send_message(chat_id, "🔐 انتهت صلاحيتك. أدخل كلمة المرور:")
        return
    
    # القائمة
    if "يومي" in text:
        bot.send_message(chat_id, "⏳ جاري طلب التحليل اليومي...")
        add_to_airtable("TOP10", chat_id)
        return
    
    if "عملة" in text:
        bot.send_message(chat_id, "🔍 أرسل رمز العملة (مثال: BTC, ETH, PEPE):")
        return
    
    # استقبال رمز العملة
    if text.replace("$", "").isalpha() and len(text) <= 10:
        coin = text.upper().replace("$", "")
        bot.send_message(chat_id, f"⏳ جاري تحليل {coin}...")
        add_to_airtable(coin, chat_id)
        return
    
    show_menu(chat_id)

print("Bot is running...")
bot.infinity_polling()
