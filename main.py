from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = '7743716121:AAEtAuZPTaEqQK4lZysmMw6tV1Kv_K_NDyc'
CHAT_ID = '5952085659'

@app.route('/')
def home():
    return 'SignalBeast bot is live'

@app.route('/send', methods=['GET'])
def send_signal():
    pair = request.args.get('pair')
    signal = request.args.get('signal')
    confidence = request.args.get('confidence')

    message = f"SignalBeast Alert:\nPair: {pair}\nSignal: {signal}\nWin Chance: {confidence}%"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {'chat_id': CHAT_ID, 'text': message}

    requests.post(url, data=data)
    return 'Signal sent!'
       
   
