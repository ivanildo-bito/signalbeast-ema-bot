import requests
from flask import Flask
import time
import threading

app = Flask(__name__)

# === CONFIG ===
BOT_TOKEN = "7743716121:AAEtAuZPTaEqQK4lZysmMw6tV1Kv_K_NDyc"
CHAT_ID = "5952085659"
BINANCE_URL = "https://api.binance.com/api/v3/klines"

# === PARAMETERS ===
SYMBOLS = ["btcusdt", "gbpeur", "eurusd"]
TIMEFRAME = "5m"
INTERVAL = 300  # seconds (5 minutes)

# === TELEGRAM FUNCTION ===
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=payload)
        print(f"Telegram status: {response.status_code}, msg: {message}")
    except Exception as e:
        print(f"Telegram error: {e}")

# === INDICATOR FUNCTIONS ===
def calculate_rsi(closes, period=14):
    gains = []
    losses = []
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

# === MAIN SIGNAL FUNCTION ===
def check_signals():
    print("Starting signal check...")
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

            print(f"{symbol.upper()} | RSI: {rsi:.2f} | EMA fast: {ema_fast:.2f} | EMA slow: {ema_slow:.2f} | Alligator: {alligator}")

            action = None
            if rsi < 30 and ema_fast > ema_slow and alligator == "BUY":
                action = "BUY"
            elif rsi > 70 and ema_fast < ema_slow and alligator == "SELL":
                action = "SELL"

            if action:
                message = (
                    f"{symbol.upper()} SIGNAL: {action}\n"
                    f"RSI: {rsi:.2f}\n"
                    f"EMA Fast: {ema_fast:.2f}\n"
                    f"EMA Slow: {ema_slow:.2f}"
                )
                send_telegram_message(message)
            else:
                print(f"{symbol.upper()} | No signal.")
        except Exception as e:
            print(f"Error processing {symbol}: {e}")

# === BACKGROUND LOOP ===
def run_bot():
    while True:
        check_signals()
        time.sleep(INTERVAL)

# === START THREAD ON LAUNCH ===
if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=5000)

     
