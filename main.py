import requests
import pandas as pd
import time

# === INSTELLINGEN ===
PAIR = 'BTCUSDT'
INTERVAL = '1m'
LIMIT = 100

EMA_FAST = 9
EMA_SLOW = 21

TELEGRAM_TOKEN = '7743716121:AAEtAuZPTaEqQK4lZysmMw6tV1Kv_K_NDyc'
CHAT_ID = '5952085659'

last_signal = None

def get_candles():
    url = f'https://api.binance.com/api/v3/klines?symbol={PAIR}&interval={INTERVAL}&limit={LIMIT}'
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        'time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])
    df['close'] = pd.to_numeric(df['close'])
    return df

def send_signal(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def check_ema_strategy():
    global last_signal
    df = get_candles()
    df['EMA_FAST'] = df['close'].ewm(span=EMA_FAST, adjust=False).mean()
    df['EMA_SLOW'] = df['close'].ewm(span=EMA_SLOW, adjust=False).mean()

    if df['EMA_FAST'].iloc[-2] < df['EMA_SLOW'].iloc[-2] and df['EMA_FAST'].iloc[-1] > df['EMA_SLOW'].iloc[-1]:
        if last_signal != 'BUY':
            send_signal("SignalBeast: KOOPSIGNAAL - EMA9 kruist boven EMA21 op BTCUSDT")
            last_signal = 'BUY'

    elif df['EMA_FAST'].iloc[-2] > df['EMA_SLOW'].iloc[-2] and df['EMA_FAST'].iloc[-1] < df['EMA_SLOW'].iloc[-1]:
        if last_signal != 'SELL':
            send_signal("SignalBeast: VERKOOPSIGNAAL - EMA9 kruist onder EMA21 op BTCUSDT")
            last_signal = 'SELL'

# === LOOP ===
while True:
    try:
        check_ema_strategy()
        time.sleep(60)
    except Exception as e:
        print(f"Fout: {e}")
        time.sleep(60)
