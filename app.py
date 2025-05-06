import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

WHAPI_TOKEN = 'YflrQ8qtahEndXwrULX79EnvgSTCtjfi'
WHAPI_URL = 'https://gate.whapi.cloud'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    print('Recebido:', json.dumps(data, indent=2))

    if 'messages' in data.get('event', {}):
        message_data = data['event']['messages'][0]
        chat_id = message_data.get('from')  # <<< TROCA AQUI
        body = message_data.get('text', {}).get('body')

        if chat_id and body:
            reply_text = f"🔮 Recebi sua mensagem: {body}. Logo mais respondo!"

            response = requests.post(
                f'{WHAPI_URL}/messages/text',
                headers={'Authorization': f'Bearer {WHAPI_TOKEN}', 'Content-Type': 'application/json'},
                json={
                    'to': chat_id,
                    'body': reply_text
                }
            )

            print('Resposta enviada:', response.status_code, response.text)
            return jsonify({'status': 'message sent'}), 200

    return jsonify({'status': 'no action taken'}), 200

if __name__ == '__main__':
    app.run(port=5000)
