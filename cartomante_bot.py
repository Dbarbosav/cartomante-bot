from flask import Flask, request, jsonify
import requests
import openai
import pytz
from datetime import datetime

app = Flask(__name__)

# Sua chave de API da OpenAI (você precisa gerar no site deles)
openai.api_key = "SUA_API_KEY_AQUI"

# Função para gerar a resposta da IA
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
        model="gpt-4o",  # Ou "gpt-3.5-turbo" se quiser economizar
        messages=[
            {"role": "system", "content": prompt_base},
            {"role": "user", "content": pergunta_usuario}
        ],
        max_tokens=400,
        temperature=0.8,
    )

    return response['choices'][0]['message']['content'].strip()

# Webhook do WhatsApp
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    # Pegando a mensagem recebida
    mensagem_usuario = data['messages'][0]['text']['body']
    numero_cliente = data['messages'][0]['from']

    # (Opcional) Extrair nome e data se quiser captar do WhatsApp depois
    nome_cliente = "Cliente"
    data_nascimento_cliente = None  # Pode melhorar se pedir no fluxo inicial

    resposta_gerada = gerar_resposta_ia(mensagem_usuario, nome_cliente, data_nascimento_cliente)

    # Simular envio da resposta (trocar pela integração real do WhatsApp API que você estiver usando)
    print(f"Mensagem para {numero_cliente}: {resposta_gerada}")

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(port=5000)
