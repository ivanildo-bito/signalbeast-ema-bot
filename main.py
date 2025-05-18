import requests
from flask import Flask
import threading
import time

app = Flask(__name__)

# === TELEGRAM CONFIG ===
BOT_TOKEN = "7743716121:AAEtAuZPTaEqQK4lZysmMw6tV1Kv_K_NDyc"
CHAT_ID = "5952085659"

# === MARKTCONFIGURATIE ===
SYMBOLS = ["BTCUSDT", "ETHUSDT", "XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]
TIMEFRAME = "5"
CHECK_INTERVAL = 300  # elke 5 minuten

# === BYBIT KLINE API ===
def fetch_klines(symbol):
    url = f"https://api.bybit.com/v5/market/kline"
    params = {
        "category": "linear",
        "symbol": symbol,
        "interval": TIMEFRAME,
        "limit": 30
    }
    try:
        response = requests.get(url, params=params)
        candles = response.json().get("result", {}).get("list", [])
        closes = [float(c[4]) for c in candles]
        return closes
    except Exception as e:
        print(f"Fout bij ophalen data voor {symbol}: {e}")
        return []

# === INDICATOREN ===
def calculate_rsi(closes, period=14):
    if len(closes) < period:
        return 50
    gains, losses = [], []
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i - 1]
        gains.append(max(delta, 0))
        losses.append(max(-delta, 0))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_ema(prices, period):
    ema = prices[0]
    k = 2 / (period + 1)
    for price in prices[1:]:
        ema = price * k + ema * (1 - k)
    return ema

def alligator_signal(prices):
    if prices[-1] > prices[-2] > prices[-3]:
        return "BUY"
    elif prices[-1] < prices[-2] < prices[-3]:
        return "SELL"
    else:
        return "HOLD"

# === SIGNALEN CONTROLEREN ===
def check_signals():
    for symbol in SYMBOLS:
        closes = fetch_klines(symbol)
        if len(closes) < 21:
            continue
        rsi = calculate_rsi(closes)
        ema_fast = calculate_ema(closes[-10:], 10)
        ema_slow = calculate_ema(closes[-21:], 21)
        alligator = alligator_signal(closes[-3:])

        action = None
        if rsi < 30 and ema_fast > ema_slow and alligator == "BUY":
            action = "BUY"
        elif rsi > 70 and ema_fast < ema_slow and alligator == "SELL":
            action = "SELL"
        else:
            action = "HOLD"

        message = f"{symbol}\nRSI: {round(rsi, 2)}\nEMA: {round(ema_fast, 2)} / {round(ema_slow, 2)}\nAlligator: {alligator}\nSignal: {action}"
        send_telegram(message)

# === TELEGRAM STUREN ===
def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Fout bij verzenden Telegram: {e}")

# === LOOP STARTEN ===
def run_bot():
    while True:
        check_signals()
        time.sleep(CHECK_INTERVAL)

threading.Thread(target=run_bot).start()

@app.route('/')
def home():
    return "SignalBeast Telegram bot draait!"

  
     
