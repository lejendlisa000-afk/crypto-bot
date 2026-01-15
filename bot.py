import telebot
import requests
from datetime import datetime

BOT_TOKEN = "8481866188:AAGN9xGupU0yDrUZSqwDf4ZAE_LYiolmGNE"
AIRTABLE_TOKEN = "patz21qaZoRloAnBC.bf6fccdfb2075958857b96dd78de8411e781a9b6ca4fd16a680b1fb9f8f3b57d"
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
                "status": "pending",
                "timestamp": datetime.now().isoformat()
            }
        }]
    }
    requests.post(url, headers=headers, json=data)

@bot.message_handler(commands=['start'])
def welcome(message):
    text = """🤖 مرحباً بك في محلل العملات الذكي!

أرسل لي رمز أي عملة وسأحللها لك بدقة عالية.

أمثلة: BTC, ETH, PEPE, SHIB

📊 ستحصل على:
✅ تحليل السيولة والحجم
✅ 3 أهداف محافظة
✅ وقف خسارة دقيق (≤3%)
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
