import time
import requests
import ta
import pandas as pd
from flask import Flask

# Telegram gegevens
BOT_TOKEN = "7743716121:AAEtAuZPTaEqQK4lZysmMw6tV1Kv_K_NDyc"
CHAT_ID = "5952085659"

# Maak een Flask app
app = Flask(_name_)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Fout bij verzenden bericht: {e}")

def get_binance_data(symbol="GBPEUR", interval="5m", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url)
        data = response.json()
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_vol', 'taker_buy_quote_vol', 'ignore'
        ])
        df['close'] = pd.to_numeric(df['close'])
        return df
    except Exception as e:
        print(f"Fout bij ophalen data: {e}")
        return None

def analyze_and_signal():
    df = get_binance_data("GBPEUR", "5m")
    if df is None:
        return

    df['rsi'] = ta.momentum.RSIIndicator(close=df['close']).rsi()
    df['ema'] = ta.trend.EMAIndicator(close=df['close'], window=21).ema_indicator()

    # Alligator indicator
    df['jaw'] = df['close'].rolling(window=13).mean()
    df['teeth'] = df['close'].rolling(window=8).mean()
    df['lips'] = df['close'].rolling(window=5).mean()

    latest = df.iloc[-1]
    
    if latest['rsi'] < 30 and latest['close'] > latest['ema'] and latest['lips'] > latest['teeth'] > latest['jaw']:
        send_telegram_message("KOOPSIGNAAL: GBPEUR\nRSI: laag, prijs boven EMA, Alligator bullish.")
    elif latest['rsi'] > 70 and latest['close'] < latest['ema'] and latest['lips'] < latest['teeth'] < latest['jaw']:
        send_telegram_message("VERKOOPSIGNAAL: GBPEUR\nRSI: hoog, prijs onder EMA, Alligator bearish.")

@app.route('/')
def home():
    return "SignalBeast bot is LIVE!"

@app.route('/run')
def run_bot():
    analyze_and_signal()
    return "Analyse uitgevoerd en eventueel signaal verzonden."

if _name_ == '_main_':
    app.run(host='0.0.0.0', port=10000)
