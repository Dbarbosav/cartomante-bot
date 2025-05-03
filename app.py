from flask import Flask, request, jsonify
import openai
import os
import logging
import requests
from datetime import datetime

app = Flask(__name__)

# Configurações
openai.api_key = os.getenv('OPENAI_API_KEY')
GPT_MODEL = "gpt-3.5-turbo"
WPP_SERVER_URL = os.getenv('WPP_SERVER_URL')
WPP_SESSION_NAME = os.getenv('WPP_SESSION_NAME')  # opcional, se usar na API

# Logs
logging.basicConfig(
    filename='cartomante.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Dados dos Cartomantes
CARD_READERS = {
    '1': {'name': 'Pai Oswaldo', 'emoji': '👴🏻'},
    '2': {'name': 'Dona Margareth', 'emoji': '👵🏻'}
}

# Pacotes de Consulta
PACKAGES = {
    '1': {'name': '1 pergunta gratuita', 'price': 0, 'questions': 1},
    '2': {'name': '3 perguntas', 'price': 9.90, 'questions': 3},
    '3': {'name': '5 perguntas', 'price': 14.90, 'questions': 5},
    '4': {'name': 'Mapa Astral', 'price': 14.90, 'questions': 1}
}

# Sessões (em memória)
sessions = {}

# Função OpenAI
def generate_gpt_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "Você é um cartomante espiritual. Use linguagem mística, emojis e responda em português brasileiro."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message['content']
    except Exception as e:
        logging.error(f"Erro OpenAI: {str(e)}")
        return "🔮 Os espíritos estão ocupados agora. Tente novamente mais tarde."

# Enviar mensagem via WPPConnect
def send_whatsapp_message(phone, text):
    payload = {
        "phone": phone,
        "message": text
    }
    try:
        response = requests.post(f"{WPP_SERVER_URL}/api/send-message", json=payload)
        response.raise_for_status()
        logging.info(f"Mensagem enviada para {phone}: {text[:50]}...")
    except Exception as e:
        logging.error(f"Erro ao enviar mensagem para {phone}: {e}")

# Mensagem de Boas-vindas
def get_welcome_message():
    return """🔮 *Bem-vindo ao Cartomante Pro!*

Escolha seu cartomante:
1️⃣ Pai Oswaldo 👴🏻  
2️⃣ Dona Margareth 👵🏻

Digite o número do cartomante."""

# Webhook principal
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    phone = data['data']['phone']
    message = data['data']['message'].strip().lower()

    if phone not in sessions:
        sessions[phone] = {
            'cartomante': None,
            'package': None,
            'questions_asked': 0,
            'max_questions': 0
        }

    session = sessions[phone]

    # Fluxo: escolha cartomante
    if session['cartomante'] is None:
        if message in CARD_READERS:
            session['cartomante'] = CARD_READERS[message]
            reply = f"✨ Você escolheu {session['cartomante']['name']} {session['cartomante']['emoji']}\n\nAgora escolha um pacote:\n1️⃣ 1 pergunta gratuita\n2️⃣ 3 perguntas - R$ 9,90\n3️⃣ 5 perguntas - R$ 14,90\n4️⃣ Mapa Astral - R$ 14,90\n\nDigite o número do pacote."
        else:
            reply = get_welcome_message()
        send_whatsapp_message(phone, reply)
        return jsonify({'status': 'ok'})

    # Fluxo: escolha pacote
    if session['package'] is None:
        if message in PACKAGES:
            session['package'] = PACKAGES[message]
            session['max_questions'] = session['package']['questions']
            reply = f"🔮 Você escolheu o pacote: *{session['package']['name']}*. Pode enviar sua pergunta agora! ✨"
        else:
            reply = "❌ Pacote inválido. Por favor, escolha um dos pacotes disponíveis (1, 2, 3 ou 4)."
        send_whatsapp_message(phone, reply)
        return jsonify({'status': 'ok'})

    # Fluxo: responder perguntas
    if session['questions_asked'] < session['max_questions']:
        gpt_response = generate_gpt_response(message)
        session['questions_asked'] += 1

        if session['questions_asked'] >= session['max_questions']:
            upsell = "⚠️ Você atingiu o limite do seu pacote. Para continuar sua jornada espiritual, acesse nosso portal: [link_para_pagamento] 🔮✨"
            full_response = f"{gpt_response}\n\n{upsell}"
        else:
            full_response = gpt_response

        send_whatsapp_message(phone, full_response)
        return jsonify({'status': 'ok'})

    else:
        reply = "⚠️ Você já utilizou todas as perguntas do seu pacote. Para continuar, acesse nosso portal: [link_para_pagamento] ✨"
        send_whatsapp_message(phone, reply)
        return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
