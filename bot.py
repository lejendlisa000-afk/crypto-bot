import telebot
import requests
from datetime import datetime

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
    response = requests.post(url, headers=headers, json=data)
    print(f"Airtable response: {response.status_code}")

@bot.message_handler(commands=['start'])
def welcome(message):
    text = """🔐 مرحباً بك في محلل العملات الذكي!

⚠️ هذا البوت محمي بكلمة مرور.

أرسل كلمة المرور للدخول:"""
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()
    
    # التحقق من الباسورد
    if chat_id not in authorized_users:
        if text == PASSWORD:
            authorized_users.add(chat_id)
            bot.send_message(chat_id, """✅ تم التحقق بنجاح!

🤖 مرحباً بك في محلل العملات الذكي!

أرسل لي رمز أي عملة وسأحللها لك بدقة عالية.

أمثلة: BTC, ETH, PEPE, SHIB

👨‍💻 صاحب البوت: @ipr_4""")
        else:
            bot.send_message(chat_id, "❌ كلمة المرور خاطئة. حاول مرة أخرى.")
        return
    
    # المستخدم مصرح له - حلل العملة
    coin = text.upper()
    bot.send_message(chat_id, f"✅ تم استلام طلبك لتحليل {coin}\n\n⏳ سيصلك التحليل العميق خلال دقائق...")
    add_to_airtable(coin, chat_id)

print("Bot is running...")
bot.infinity_polling()
