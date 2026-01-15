import telebot
import requests

BOT_TOKEN = "8481866188:AAGN9xGupU0yDrUZSqwDf4ZAE_LYiolmGNE"
bot = telebot.TeleBot(BOT_TOKEN)

def get_crypto_data(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def analyze_coin(symbol):
    data = get_crypto_data(symbol)
    if not data:
        return f"❌ لم أجد عملة {symbol}\nتأكد من الاسم (مثال: BTC, ETH, PEPE)"
    
    price = float(data['lastPrice'])
    change = float(data['priceChangePercent'])
    volume = float(data['quoteVolume'])
    high = float(data['highPrice'])
    low = float(data['lowPrice'])
    
    # تحديد المخاطرة
    if change < -5:
        risk = "🔴 عالي جداً (9/10)"
        recommendation = "❌ تجنب"
    elif change < -2:
        risk = "🟠 عالي (7/10)"
        recommendation = "⏳ انتظار"
    elif change < 0:
        risk = "🟡 متوسط (5/10)"
        recommendation = "⏳ انتظار"
    else:
        risk = "🟢 منخفض (3/10)"
        recommendation = "✅ دخول محافظ"
    
    # حساب الأهداف ووقف الخسارة
    target1 = price * 1.02
    target2 = price * 1.04
    target3 = price * 1.06
    stop_loss = price * 0.97
    
    # تنسيق الرسالة
    msg = f"""
🪙 **العملة:** {symbol}/USDT
💰 **السعر:** ${price:.6f}
📊 **التغير 24س:** {change:.2f}%
📈 **الحجم:** ${volume:,.0f}
⬆️ **أعلى سعر:** ${high:.6f}
⬇️ **أدنى سعر:** ${low:.6f}

⚠️ **مستوى المخاطرة:** {risk}

🎯 **الأهداف:**
1️⃣ ${target1:.6f}
2️⃣ ${target2:.6f}
3️⃣ ${target3:.6f}

🛑 **وقف الخسارة:** ${stop_loss:.6f} (-3%)

✅ **التوصية:** {recommendation}

⚠️ **تنبيه:** هذا تحليل آلي. قم بالبحث الخاص قبل الدخول.

👨‍💻 صاحب البوت: @ipr_4
"""
    return msg

@bot.message_handler(commands=['start'])
def welcome(message):
    text = """🤖 **مرحباً بك في محلل العملات الذكي!**

أرسل لي رمز أي عملة وسأحللها لك فوراً.

**أمثلة:**
- BTC - بيتكوين
- ETH - إيثريوم
- PEPE - بيبي
- SHIB - شيبا

📊 سأعطيك:
✅ السعر والتغير
✅ 3 أهداف محاف
