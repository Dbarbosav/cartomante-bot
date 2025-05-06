import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WHAPI_TOKEN = os.getenv("WHAPI_TOKEN")
WHAPI_URL = "https://api.whapi.cloud/messages/sendText"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS_WHAPI = {
    "Authorization": f"Bearer {WHAPI_TOKEN}",
    "Content-Type": "application/json"
}

HEADERS_GROQ = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data or 'messages' not in data:
        return jsonify({"error": "No message received"}), 400

    message_info = data['messages'][0]
    chat_id = message_info.get('chat_id')
    user_message = message_info.get('text', {}).get('body')

    if not chat_id or not user_message:
        return jsonify({"error": "Invalid message format"}), 400

    print(f"Mensagem recebida de {chat_id}: {user_message}")

    prompt = f"Você é uma cartomante mística chamada Dona Margareth. Responda de forma espiritualizada e acolhedora. Pergunta: {user_message}"

    payload_groq = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "system", "content": "Você é uma cartomante experiente."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    response_groq = requests.post(GROQ_API_URL, headers=HEADERS_GROQ, json=payload_groq)

    if response_groq.status_code != 200:
        print(f"Erro Groq: {response_groq.status_code} - {response_groq.text}")
        reply_text = "Desculpe, estou com dificuldades técnicas no momento. 🙏"
    else:
        groq_data = response_groq.json()
        reply_text = groq_data["choices"][0]["message"]["content"].strip()

    payload_whapi = {
        "to": chat_id,
        "text": reply_text
    }

    response_whapi = requests.post(WHAPI_URL, headers=HEADERS_WHAPI, json=payload_whapi)

    if response_whapi.status_code != 200:
        print(f"Erro Whapi: {response_whapi.status_code} - {response_whapi.text}")

    return jsonify({"status": "mensagem enviada"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
