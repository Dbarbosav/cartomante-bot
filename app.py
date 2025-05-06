import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Variáveis de ambiente
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WHAPI_TOKEN = os.getenv("WHAPI_TOKEN")
WHAPI_URL = os.getenv("WHAPI_URL", "https://wa.whapi.cloud/messages/sendText")
GROQ_URL = os.getenv("GROQ_URL", "https://api.groq.com/openai/v1/chat/completions")

# Função para gerar resposta da Groq
def gerar_resposta_groq(mensagem_usuario):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",  # Modelo atualizado e suportado
        "messages": [
            {"role": "system", "content": "Você é um cartomante experiente chamado Pai Oswaldo ou Dona Margareth."},
            {"role": "user", "content": mensagem_usuario}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=data)
        response.raise_for_status()
        resultado = response.json()
        resposta_texto = resultado['choices'][0]['message']['content'].strip()
        return resposta_texto
    except Exception as e:
        print(f"Erro na Groq: {e}")
        return "Desculpe, estou com dificuldades para responder no momento. Tente novamente mais tarde."

# Rota do webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.json
    print(f"Mensagem recebida: {payload}")

    try:
        mensagens = payload.get('messages', [])
        if not mensagens:
            return jsonify({"status": "ignored"})

        mensagem = mensagens[0]
        texto_recebido = mensagem.get('text', {}).get('body')
        chat_id = mensagem.get('chat_id')

        if not texto_recebido or not chat_id:
            return jsonify({"status": "invalid payload"}), 400

        # Gerar resposta
        resposta = gerar_resposta_groq(texto_recebido)

        # Enviar resposta pelo Whapi
        headers_whapi = {
            "Authorization": f"Bearer {WHAPI_TOKEN}",
            "Content-Type": "application/json"
        }
        payload_whapi = {
            "chatId": chat_id,
            "body": resposta
        }

        response_whapi = requests.post(WHAPI_URL, headers=headers_whapi, json=payload_whapi)
        print(f"Resposta Whapi: {response_whapi.status_code} - {response_whapi.text}")

    except Exception as e:
        print(f"Erro no webhook: {e}")

    return jsonify({"status": "received"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
