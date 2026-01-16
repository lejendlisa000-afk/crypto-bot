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
user_state = {}
last_coin = {}

def add_to_airtable(coin, chat_id, status="pending"):
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
                "status": status
            }
        }]
    }
    requests.post(url, headers=headers, json=data)

def main_menu(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📊 تحليل يومي (Top 10)", callback_data="daily"))
    markup.add(types.InlineKeyboardButton("🔍 تحليل عملة معينة", callback_data="coin"))
    bot.send_message(chat_id, "🤖 اختر من القائمة:", reply_markup=markup)

def entry_question(chat_id, coin):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ نعم، سأدخل", callback_data=f"yes_{coin}"),
        types.InlineKeyboardButton("❌ لا، اطلاعي", callback_data=f"no_{coin}")
    )
    bot.send_message(chat_id, "❓ هل ستدخل هذه الصفقة؟", reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if chat_id in authorized_users:
        main_menu(chat_id)
    else:
        bot.send_message(chat_id, "🔐 مرحباً!\n\nأدخل كلمة المرور للمتابعة:")
        user_state[chat_id] = "waiting_password"

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    data = call.data
    
    if chat_id not in authorized_users:
        bot.answer_callback_query(call.id, "🔐 أدخل كلمة المرور أولاً")
        return
    
    if data == "daily":
        bot.answer_callback_query(call.id, "⏳ جاري الطلب...")
        bot.send_message(chat_id, "⏳ جاري طلب التحليل اليومي لأفضل 10 عملات...")
        add_to_airtable("TOP10", chat_id)
        
    elif data == "coin":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "🔍 أرسل رمز العملة:\n\nمثال: BTC, ETH, PEPE, SOL")
        user_state[chat_id] = "waiting_coin"
        
    elif data.startswith("yes_"):
        coin = data.replace("yes_", "")
        bot.answer_callback_query(call.id, "✅ تم!")
        bot.send_message(chat_id, f"✅ سأتابع صفقة {coin} وأرسل لك التحديثات عند:\n\n• تحقق أي هدف\n• الاقتراب من وقف الخسارة\n• تغيرات مهمة")
        add_to_airtable(f"{coin}_TRACK", chat_id, "track")
        main_menu(chat_id)
        
    elif data.startswith("no_"):
        coin = data.replace("no_", "")
        bot.answer_callback_query(call.id, "👀 تم!")
        bot.send_message(chat_id, f"👀 تم! تحليل {coin} للاطلاع فقط.")
        main_menu(chat_id)
        
    elif data == "menu":
        bot.answer_callback_query(call.id)
        main_menu(chat_id)

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_state.get(chat_id, "")
    
    # انتظار الباسورد
    if state == "waiting_password" or chat_id not in authorized_users:
        if text == PASSWORD:
            authorized_users.add(chat_id)
            user_state[chat_id] = ""
            bot.send_message(chat_id, "✅ تم التحقق بنجاح!")
            main_menu(chat_id)
        else:
            bot.send_message(chat_id, "❌ كلمة المرور خاطئة. حاول مرة أخرى:")
        return
    
    # انتظار رمز العملة
    if state == "waiting_coin":
        coin = text.upper().replace("$", "").replace("USDT", "").replace("/", "")
        if coin.isalpha() and 2 <= len(coin) <= 10:
            last_coin[chat_id] = coin
            user_state[chat_id] = ""
            bot.send_message(chat_id, f"⏳ جاري تحليل {coin}...")
            add_to_airtable(coin, chat_id)
            # السؤال سيأتي بعد التحليل من Twin
        else:
            bot.send_message(chat_id, "❌ رمز غير صحيح. أرسل رمز عملة صحيح (مثل BTC):")
        return
    
    # أي رسالة أخرى
    main_menu(chat_id)

print("Bot is running...")
bot.infinity_polling()
