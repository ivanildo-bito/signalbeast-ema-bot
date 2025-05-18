from flask import Flask, request
import requests
import os

app = Flask(_name_)

# Telegram
TELEGRAM_TOKEN = "7743716121:AAEtAuZPTaEqQK4lZysmMw6tV1Kv_K_NDyc"
TELEGRAM_CHAT_ID = "5952085659"

@app.route('/')
def home():
    return "SignalBeast staat online!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data is None:
        return "Geen data ontvangen", 400

    # Bericht bouwen
    message = f"*Nieuw signaal via SignalBeast*\n\n"
    if 'ticker' in data:
        message += f"Pair: {data['ticker']}\n"
    if 'strategy' in data and 'order_action' in data['strategy']:
        message += f"Actie: {data['strategy']['order_action'].capitalize()}\n"
    if 'price' in data:
        message += f"Prijs: {data['price']}"

    # Telegram verzenden
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

    return "Signaal verzonden!", 200

# Belangrijk voor Render (herkenning poort)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
