from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Token correto da Whapi
TOKEN = "YflrQ8qtahEndXwrULX79EnvgSTCtjfi"

API_URL = "https://gate.whapi.cloud"

@app.route("/", methods=["GET"])
def home():
    return "Cartomante Bot online!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Recebido:", data)

    if data and 'messages' in data:
        for message in data['messages']:
            chat_id = message['chatId']
            text = message.get('text', {}).get('body', '')

            resposta = f"Olá! Você disse: {text}"
            send_message(chat_id, resposta)

    return jsonify({"status": "success"}), 200

def send_message(chat_id, text):
    url = f"{API_URL}/message/text"
    payload = {
        "to": chat_id,
        "body": text
    }
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    print(f"Mensagem enviada: {response.status_code}, {response.text}")

if __name__ == "__main__":
    app.run(port=5000)
