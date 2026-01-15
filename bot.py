import telebot
import requests
from datetime import datetime

BOT_TOKEN = "8106633094:AAEODJL02gcK-5VTpnXxgYDyi8anSQiJ9hQ"
AIRTABLE_TOKEN = "patnOmcrxm6o9KT2T.185f28d0b1d8e0ce28671be2edc7e441f7a5aecf0b01c01458c730693a388b21"
AIRTABLE_BASE = "appvuIfgZfQAxPsld"
AIRTABLE_TABLE = "tblkFGjUvXvIrjhcE"

bot = telebot.TeleBot(BOT_TOKEN)

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
    print(f"Airtable response: {response.status_code} - {response.text}")

@bot.message_handler(commands=['start'])
def welcome(message):
    text = """🤖 مرحباً بك في محلل العملات الذكي!

أرسل لي رمز أي عملة وسأحللها لك بدقة عالية.

أمثلة: BTC, ETH, PEPE, SHIB

📊 ستحصل على:
✅ تحليل السيولة والحجم
✅ 3 أهداف محافظة
✅ وقف خسارة دقيق
✅ الحكم الشرعي
✅ تقييم المخاطر

👨‍💻 صاحب البوت: @ipr_4"""
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: True)
def analyze(message):
    coin = message.text.upper().strip()
    chat_id = message.chat.id
    
    bot.send_message(chat_id, f"✅ تم استلام طلبك لتحليل {coin}\n\n⏳ سيصلك التحليل العميق خلال دقائق...")
    
    add_to_airtable(coin, chat_id)

print("Bot is running...")
bot.infinity_polling()

