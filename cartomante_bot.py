from flask import Flask, request, jsonify
import requests
import openai
import pytz
from datetime import datetime
import os

app = Flask(__name__)

# Pega a chave da OpenAI do ambiente seguro
openai.api_key = os.getenv("OPENAI_API_KEY")

# Função para gerar resposta da IA
def gerar_resposta_ia(pergunta_usuario, nome_usuario=None, data_nascimento=None):
    prompt_base = f"""
Você é um cartomante espiritualista muito sábio e acolhedor chamado Mestre Luz.
Seu objetivo é orientar espiritualmente quem te procura, respondendo perguntas com base na energia do universo, nas cartas e nas estrelas.
Seja sempre positivo, acolhedor e profundo nas respostas.
Fale como se estivesse realmente tirando cartas ou lendo o mapa da pessoa.
Nome da pessoa: {nome_usuario if nome_usuario else "Desconhecido"}
Data de nascimento: {data_nascimento if data_nascimento else "Não informado"}
Pergunta: {pergunta_usuario}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # Ou "gpt-3.5-turbo" se quiser usar uma versão mais barata
        messages=[
            {"role": "system", "content": prompt_base},
            {"role": "user", "content": pergunta_usuario}
        ],
        max_tokens=400,
        temperature=0.8,
    )

    return response['choices'][0]['message']['content'].strip()

# Webhook para receber mensagens do WhatsApp
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    # Pegando mensagem enviada
    mensagem_usuario = data['messages'][0]['text']['body']
    numero_cliente = data['messages'][0]['from']

    # (Opcional) Nome e data do cliente podem ser capturados depois
    nome_cliente = "Cliente"
    data_nascimento_cliente = None

    # Gera resposta pela IA
    resposta_gerada = gerar_resposta_ia(mensagem_usuario, nome_cliente, data_nascimento_cliente)

    # Simula o envio da resposta (trocar depois pela API real do WhatsApp)
    print(f"Mensagem para {numero_cliente}: {resposta_gerada}")

    return jsonify({"status": "success"}), 200

# Rodando o app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
