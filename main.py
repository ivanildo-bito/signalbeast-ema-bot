import time import requests import ta import pandas as pd import numpy as np from flask import Flask

Telegram config

BOT_TOKEN = '5952085659:AAHvJqv...'  # Vervang met jouw volledige token CHAT_ID = '5952085659'

Flask app voor render.com

app = Flask(name)

Binance API endpoint

BINANCE_URL = 'https://api.binance.com/api/v3/klines'

Functie om data op te halen

def get_data(symbol='EURGBP', interval='5m', limit=100): params = { 'symbol': symbol.upper() + 'T',  # EURGBP => EURGBPT 'interval': interval, 'limit': limit } try: response = requests.get(BINANCE_URL, params=params) data = response.json() df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qv', 'trades', 'tb_base', 'tb_quote', 'ignore']) df['close'] = pd.to_numeric(df['close']) df['high'] = pd.to_numeric(df['high']) df['low'] = pd.to_numeric(df['low']) return df except: return None

Indicatorlogica

def generate_signal(df): df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi() df['ema'] = ta.trend.EMAIndicator(df['close'], window=21).ema_indicator() df['alligator_jaw'] = df['high'].rolling(window=13).mean() df['alligator_teeth'] = df['high'].rolling(window=8).mean() df['alligator_lips'] = df['high'].rolling(window=5).mean()

latest = df.iloc[-1]

if latest['rsi'] < 30 and latest['close'] > latest['ema'] and \
   latest['alligator_lips'] > latest['alligator_teeth'] > latest['alligator_jaw']:
    return 'BUY'
elif latest['rsi'] > 70 and latest['close'] < latest['ema'] and \
     latest['alligator_lips'] < latest['alligator_teeth'] < latest['alligator_jaw']:
    return 'SELL'
else:
    return 'WAIT'

Verstuur signaal

def send_signal(signal, price): sl = price * 0.98 if signal == 'BUY' else price * 1.02 tp = price * 1.05 if signal == 'BUY' else price * 0.95

message = f"SIGNALBEAST ALERT\nPair: EUR/GBP\nSignal: {signal}\nPrice: {price:.4f}\nSL: {sl:.4f}\nTP: {tp:.4f}"
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
data = {"chat_id": CHAT_ID, "text": message}
requests.post(url, data=data)

Hoofdfunctie

@app.route('/') def check_market(): df = get_data(symbol='EURGBP') if df is not None: signal = generate_signal(df) price = df['close'].iloc[-1] if signal != 'WAIT': send_signal(signal, price) return f"Laatste signaal: {signal} @ {price}" return "Geen data"

if name == 'main': app.run(host='0.0.0.0', port=10000)
