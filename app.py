from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Seu token da Whapi
API_TOKEN = 'YflrQ8qtahEndXwrULX79EnvgSTCtjfi'
API_URL = 'https://gate.whapi.cloud/messages/text'

@app.route('/')
def home():
    return 'Cartomante bot rodando com sucesso!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Recebido:", data)

    if data.get('event', {}).get('type') == 'messages':
        messages = data.get('messages', [])
        for message in messages:
            chat_id = message.get('chat_id')
            text = message.get('text')

            if chat_id and text:
                # Resposta automática
                resposta = f"🔮 Recebi sua mensagem: {text}. Logo mais respondo!"

                payload = {
                    'to': chat_id,
                    'body': resposta
                }
                headers = {
                    'Authorization': f'Bearer {API_TOKEN}',
                    'Content-Type': 'application/json'
                }

                r = requests.post(API_URL, json=payload, headers=headers)
                print('Enviado:', r.status_code, r.text)

    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True)
