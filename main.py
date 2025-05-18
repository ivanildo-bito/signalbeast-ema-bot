from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = "7743716121:AAEtAuZPTaEqQK4lZysmMw6tV1Kv_K_NDyc"
CHAT_ID = "5952085659"  # Jouw echte chat ID

@app.route('/')
def home():
    return 'SignalBeast bot is live'

@app.route('/send', methods=['GET'])
def send_signal():
    pair = request.args.get('pair', 'Unknown Pair')
    signal = request.args.get('signal', 'No Signal')
    confidence = request.args.get('confidence', '0')

    message = f"*SignalBeast Alert*\nPair: {pair}\nSignal: {signal}\nConfidence: {confidence}%"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    response = requests.post(url, data=data)
    return f"Signal sent with status {response.status_code}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
