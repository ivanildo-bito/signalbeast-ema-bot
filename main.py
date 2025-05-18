import requests
from flask import Flask
import threading
import time

app = Flask(__name__)

# === CONFIG ===
BOT_TOKEN = "7743716121:AAEtAuZPTaEqQK4lZysmMw6tV1Kv_K_NDyc"
CHAT_ID = "5952085659"
BINANCE_URL = "https://api.binance.com/api/v3/klines"

# === PARAMETERS ===
SYMBOLS = ["btcusdt", "gbpeur", "eurusd"]
TIMEFRAME = "5m"
INTERVAL = 300  # elke 5 minuten

# === INDICATOREN ===
def calculate_rsi(closes, period=14):
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
    return "HOLD"

# === SIGNAAL FUNCTIE ===
def check_signals():
    for symbol in SYMBOLS:
        try:
            response = requests.get(BINANCE_URL, params={
                "symbol": symbol.upper(),
                "interval": TIMEFRAME,
                "limit": 30
            })
            data = response.json()
            closes = [float(candle[4]) for candle in data]
            rsi = calculate_rsi(closes)
            ema_fast = calculate_ema(closes[-10:], 10)
            ema_slow = calculate_ema(closes[-21:], 21)
            alligator = alligator_signal(closes[-3:])

            action = None
            if rsi < 30 and ema_fast > ema_slow and alligator == "BUY":
                action = "BUY"
            elif rsi > 70 and ema_fast < ema_slow and alligator == "SELL":
                action = "SELL"

            if action:
                send_signal(symbol.upper(), action)

        except Exception as e:
            print(f"Fout bij {symbol}: {e}")

def send_signal(symbol, action):
    message = f"SignalBeast Alert\nPair: {symbol}\nAction: {action}"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})
    print(f"Signaal verstuurd: {symbol} - {action}")

# === LOOP ===
def run_bot():
    while True:
        check_signals()
        time.sleep(INTERVAL)

@app.route('/')
def index():
    return "SignalBeast draait live!"

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=5000)
