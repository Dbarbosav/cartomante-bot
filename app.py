import os
import time
import json
from flask import Flask, request, jsonify
import requests
import openai

app = Flask(__name__)

# Configurações
WHAPI_TOKEN = 'YflrQ8qtahEndXwrULX79EnvgSTCtjfi'
OPENAI_API_KEY = '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'
openai.api_key = OPENAI_API_KEY

WHAPI_URL = 'https://gate.whapi.cloud'

# Função para enviar mensagem via Whapi
def send_whatsapp_message(to_number, message):
    url = f"{WHAPI_URL}/sendMessageText"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WHAPI_TOKEN}'
    }
    payload = {
        'to': to_number,
        'body': message
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Função para gerar resposta da OpenAI
def generate_cartomante_response(user_message, cartomante_name):
    prompt = f"""
    Você é um cartomante chamado {cartomante_name}, com tom místico e acolhedor. Responda a pergunta abaixo de forma intuitiva, usando sua sabedoria espiritual, e seja detalhista para parecer uma consulta real.

    Pergunta: {user_message}

    Resposta:
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}]
        )
        reply = response['choices'][0]['message']['content']
        return reply.strip()
    except Exception as e:
        return "Desculpe, estou tendo dificuldades para acessar meu plano astral agora. Tente novamente em breve."

@app.route('/', methods=['GET'])
def home():
    return 'Cartomante Bot Online!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(json.dumps(data, indent=2))

    try:
        messages = data.get('messages')
        if not messages:
            return jsonify({'status': 'no_messages'})

        for message in messages:
            sender = message['from']
            text = message['text']['body']

            # Simula um pequeno delay para parecer realista
            time.sleep(2)

            # Decide quem vai responder (Pai Oswaldo ou Dona Margareth)
            if 'oswaldo' in text.lower():
                cartomante = 'Pai Oswaldo'
            elif 'margareth' in text.lower():
                cartomante = 'Dona Margareth'
            else:
                cartomante = 'Dona Margareth'  # Padrão

            reply = generate_cartomante_response(text, cartomante)
            
            # Envia a resposta
            send_whatsapp_message(sender, reply)

        return jsonify({'status': 'success'})

    except Exception as e:
        print(f'Erro: {e}')
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
