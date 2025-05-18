from flask import Flask, request
import os

app = Flask(_name_)

@app.route('/', methods=['GET'])
def home():
    return "SignalBeast webhook is actief!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Webhook ontvangen:", data)
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
