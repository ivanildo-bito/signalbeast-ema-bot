import requests
import time
import numpy as np

BINANCE_URL = "https://api.binance.com/api/v3/klines"
SYMBOL = "BTCUSDT"
INTERVAL = "1m"
LIMIT = 100

WEBHOOK_URL = "https://signalbeast-ema-bot.onrender.com"

FAST_EMA = 5
SLOW_EMA = 14

def get_price_data():
    params = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "limit": LIMIT
    }
    response = requests.get(BINANCE_URL, params=params)
    data = response.json()
    closes = [float(candle[4]) for candle in data]
    return np.array(closes)

def ema(data, period):
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    return np.convolve(data, weights, mode='valid')

def check_signal():
    closes = get_price_data()
    if len(closes) < SLOW_EMA:
        return None

    fast = ema(closes, FAST_EMA)[-1]
    slow = ema(closes, SLOW_EMA)[-1]

    if fast > slow:
        return "BUY"
    elif fast < slow:
        return "SELL"
    return None

def send_signal(signal):
    data = {
        "signal": signal,
        "pair": SYMBOL,
        "strategy": "EMA Crossover"
    }
    try:
        requests.post(WEBHOOK_URL, json=data)
        print(f"Signal sent: {signal}")
    except Exception as e:
        print("Error sending signal:", e)

if __name__ == "__main__":
    print("SignalBeast EMA bot started...")
    while True:
        signal = check_signal()
        if signal:
            send_signal(signal)
        time.sleep(60)

