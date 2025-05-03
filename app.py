# app.py - Código Principal (Flask + OpenAI)
from flask import Flask, request, jsonify
import openai
import os
import logging
from datetime import datetime

app = Flask(__name__)

# Configurações
openai.api_key = os.getenv('OPENAI_API_KEY')
GPT_MODEL = "gpt-3.5-turbo"
WPP_SERVER_URL = os.getenv('WPP_SERVER_URL')

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
    '1': {'name': '1 pergunta', 'price': 0, 'questions': 1},
    '2': {'name': '3 perguntas', 'price': 7.99, 'questions': 3},
    '3': {'name': '5 perguntas', 'price': 9.99, 'questions': 5},
    '4': {'name': 'Mapa Astral', 'price': 14.99, 'questions': 1},
    '5': {'name': 'Tiragem Completa', 'price': 14.99, 'questions': 1}
}

# Armazenamento simples (em produção use um banco de dados)
sessions = {}

# --- Funções da OpenAI ---
def generate_gpt_response(prompt):
    """Gera respostas místicas usando GPT-3.5"""
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

# --- Rotas do Flask ---
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    phone = data['data']['phone']
    message = data['data']['message'].lower().strip()

    # Inicia sessão se não existir
    if phone not in sessions:
        sessions[phone] = {
            'cartomante': None,
            'package': None,
            'questions_asked': 0
        }

    # Lógica do Fluxo
    response = handle_message(phone, message)
    
    # Envia resposta via WPPConnect (simplificado)
    send_whatsapp_message(phone, response)
    
    return jsonify({"status": "success"})

def handle_message(phone, message):
    session = sessions[phone]
    
    # Fluxo Principal
    if message == 'menu':
        return get_welcome_message()
    
    if not session['cartomante']:
        return handle_cartomante_choice(phone, message)
    
    if not session['package']:
        return handle_package_choice(phone, message)
    
    # ... (restante do fluxo igual ao código anterior)

# --- Funções de Resposta ---
def get_welcome_message():
    return """🔮 *Bem-vindo ao Cartomante Pro!*

Escolha seu cartomante:
1️⃣ Pai Oswaldo 👴🏻  
2️⃣ Dona Margareth 👵🏻"""

def send_whatsapp_message(phone, text):
    """Envia mensagem via API do WPPConnect"""
    logging.info(f"Enviando para {phone}: {text[:50]}...")
    # Implemente a chamada real à API do WPPConnect aqui
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)