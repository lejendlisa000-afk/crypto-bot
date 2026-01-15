import telebot

BOT_TOKEN = "8481866188:AAGN9xGupU0yDrUZSqwDf4ZAE_LYiolmGNE"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    text = """🤖 مرحباً بك في محلل العملات الذكي!

أرسل لي اسم أي عملة وسأحللها لك.
مثال: BTC أو ETH أو PEPE

👨‍💻 صاحب البوت: @ipr_4"""
    bot.reply_to(message, text)

@bot.message_handler(func=lambda m: True)
def analyze(message):
    coin = message.text.upper().strip()
    bot.reply_to(message, f"⏳ جاري تحليل {coin}...")

print("Bot is running...")
bot.infinity_polling()
