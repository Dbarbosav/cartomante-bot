import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Variáveis de ambiente
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
WHAPI_TOKEN = os.getenv('WHAPI_TOKEN')
WHAPI_URL = 'https://gate.whapi.cloud/messages/sendText'
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(f"Mensagem recebida: {data}")

    try:
        message = data['messages'][0]
        user_message = message['text']['body']
        chat_id = message['chat_name'] if 'chat_name' in message else message['chatId']

        # Integração com a IA (Groq)
        headers_groq = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }

        payload_groq = {
            "model": "mixtral-8x7b-32768",
            "messages": [
                {"role": "system", "content": "Você é um cartomante espiritual chamado Dona Margareth e responde de forma mística."},
                {"role": "user", "content": user_message}
            ]
        }

        response_groq = requests.post(GROQ_URL, headers=headers_groq, json=payload_groq)
        response_data = response_groq.json()
        print(f"Resposta Groq: {response_data}")

        if 'choices' in response_data and len(response_data['choices']) > 0:
            resposta = response_data['choices'][0]['message']['content']
        else:
            resposta = "🔮 Desculpe, não consegui interpretar sua mensagem agora. Tente novamente mais tarde."

        # Enviar resposta pelo Whapi
        headers_whapi = {
            "Authorization": f"Bearer {WHAPI_TOKEN}",
            "Content-Type": "application/json"
        }

        payload_whapi = {
            "to": message['from'],
            "body": resposta
        }

        response_whapi = requests.post(WHAPI_URL, headers=headers_whapi, json=payload_whapi)
        print(f"Resposta Whapi: {response_whapi.status_code} - {response_whapi.text}")

    except Exception as e:
        print(f"Erro: {e}")

    return jsonify({'status': 'received'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
