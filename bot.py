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

# حفظ حالة المستخدمين
user_states = {}
authorized_users = set()
pending_coins = {}

def add_to_airtable(coin, chat_id, track=False):
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
                "status": "track" if track else "pending"
            }
        }]
    }
    requests.post(url, headers=headers, json=data)

def show_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton("📊 تحليل يومي (Top 10)")
    btn2 = types.KeyboardButton("🔍 تحليل عملة معينة")
    markup.add(btn1, btn2)
    bot.send_message(chat_id, "✅ اختر ما تريد:", reply_markup=markup)

@bot.message_handler(commands=['start'])
def welcome(message):
    chat_id = message.chat.id
    user_states[chat_id] = "waiting_password"
    
    markup = types.ReplyKeyboardRemove()
    bot.send_message(chat_id, """🔐 مرحباً بك في محلل العملات الذكي!

⚠️ هذا البوت محمي بكلمة مرور.

أرسل كلمة المرور للدخول:""", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_states.get(chat_id, "waiting_password")
    
    # حالة انتظار الباسورد
    if state == "waiting_password":
        if text == PASSWORD:
            authorized_users.add(chat_id)
            user_states[chat_id] = "main_menu"
            bot.send_message(chat_id, "✅ تم التحقق بنجاح!")
            show_main_menu(chat_id)
        else:
            bot.send_message(chat_id, "❌ كلمة المرور خاطئة. حاول مرة أخرى.")
        return
    
    # التحقق من التصريح
    if chat_id not in authorized_users:
        user_states[chat_id] = "waiting_password"
        bot.send_message(chat_id, "🔐 أرسل كلمة المرور أولاً:")
        return
    
    # القائمة الرئيسية
    if text == "📊 تحليل يومي (Top 10)" or text == "1":
        user_states[chat_id] = "main_menu"
        bot.send_message(chat_id, "⏳ جاري طلب التحليل اليومي لأفضل 10 عملات...")
        add_to_airtable("TOP10_DAILY", chat_id, track=False)
        bot.send_message(chat_id, "✅ تم! سيصلك التحليل خلال دقيقة.")
        show_main_menu(chat_id)
        return
    
    if text == "🔍 تحليل عملة معينة" or text == "2":
        user_states[chat_id] = "waiting_coin"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton("🔙 رجوع")
        markup.add(btn)
        bot.send_message(chat_id, """🔍 أرسل رمز العملة التي تريد تحليلها:

مثال: BTC, ETH, PEPE, SHIB""", reply_markup=markup)
        return
    
    if text == "🔙 رجوع":
        user_states[chat_id] = "main_menu"
        show_main_menu(chat_id)
        return
    
    # انتظار اسم العملة
    if state == "waiting_coin":
        coin = text.upper()
        if coin == "🔙 رجوع":
            user_states[chat_id] = "main_menu"
            show_main_menu(chat_id)
            return
        
        pending_coins[chat_id] = coin
        user_states[chat_id] = "waiting_entry_confirm"
        
        bot.send_message(chat_id, f"⏳ جاري تحليل {coin}...")
        add_to_airtable(coin, chat_id, track=False)
        
        # سؤال هل دخلت الصفقة
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton("✅ نعم، دخلت الصفقة")
        btn2 = types.KeyboardButton("👀 لا، اطلاعي فقط")
        markup.add(btn1, btn2)
        bot.send_message(chat_id, "❓ هل ستدخل هذه الصفقة؟", reply_markup=markup)
        return
    
    # تأكيد الدخول
    if state == "waiting_entry_confirm":
        coin = pending_coins.get(chat_id, "")
        
        if "نعم" in text or "دخلت" in text:
            add_to_airtable(coin, chat_id, track=True)
            bot.send_message(chat_id, f"""✅ تم تفعيل المتابعة لعملة {coin}!

📢 سأرسل لك إشعارات عند:
- تحقق أي هدف
- الاقتراب من وقف الخسارة
- تغيرات مهمة في السعر

🔔 ابقَ متابعاً!""")
            user_states[chat_id] = "main_menu"
            show_main_menu(chat_id)
        
        elif "لا" in text or "اطلاعي" in text:
            bot.send_message(chat_id, f"👀 تم! تحليل {coin} للاطلاع فقط.\n\nلن أرسل إشعارات متابعة.")
            user_states[chat_id] = "main_menu"
            show_main_menu(chat_id)
        
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton("✅ نعم، دخلت الصفقة")
            btn2 = types.KeyboardButton("👀 لا، اطلاعي فقط")
            markup.add(btn1, btn2)
            bot.send_message(chat_id, "❓ اختر من الأزرار:", reply_markup=markup)
        return
    
    # أي رسالة أخرى
    show_main_menu(chat_id)

print("Bot is running...")
bot.infinity_polling()
