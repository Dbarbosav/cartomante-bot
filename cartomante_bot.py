from flask import Flask, request, jsonify
import requests
import openai
import pytz
from datetime import datetime
import os

app = Flask(__name__)

# Pega a chave da OpenAI do ambiente seguro
openai.api_key = os.getenv("OPENAI_API_KEY")

# Controle de perguntas e cartomante por cliente (armazenado em memória)
limite_perguntas = 3
perguntas_clientes = {}
cartomantes_clientes = {}  # Novo: Armazena o cartomante escolhido

# Função para gerar resposta da IA baseado no cartomante
def gerar_resposta_ia(pergunta_usuario, cartomante, nome_usuario=None, data_nascimento=None):
    if cartomante == "Pai Oswaldo":
        estilo_cartomante = """
Você é Pai Oswaldo, um cartomante espiritualista experiente e firme.
Suas respostas são sábias, diretas e transmitem confiança, como um verdadeiro guia espiritual.
"""
    else:  # Se for Dona Margareth
        estilo_cartomante = """
Você é Dona Margareth, uma cartomante espiritualista acolhedora e doce.
Suas respostas são cheias de carinho, esperança e conforto, trazendo paz para quem te procura.
"""

    prompt_base = f"""
{estilo_cartomante}
Nome da pessoa: {nome_usuario if nome_usuario else "Desconhecido"}
Data de nascimento: {data_nascimento if data_nascimento else "Não informado"}
Pergunta: {pergunta_usuario}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o",
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
    mensagem_usuario = data['messages'][0]['text']['body'].strip()
    numero_cliente = data['messages'][0]['from']

    # Capturar nome do cliente, se disponível
    nome_cliente = data['messages'][0].get('sender', {}).get('name', 'Cliente')
    data_nascimento_cliente = None

    # Se o cliente ainda não escolheu o cartomante, pedir para escolher
    if numero_cliente not in cartomantes_clientes:
        if mensagem_usuario in ["1", "Pai Oswaldo"]:
            cartomantes_clientes[numero_cliente] = "Pai Oswaldo"
            resposta_gerada = f"Você escolheu Pai Oswaldo! 🔮 Vamos iniciar sua leitura espiritual. Faça sua pergunta."
        elif mensagem_usuario in ["2", "Dona Margareth"]:
            cartomantes_clientes[numero_cliente] = "Dona Margareth"
            resposta_gerada = f"Você escolheu Dona Margareth! 🔮 Vamos iniciar sua leitura espiritual. Faça sua pergunta."
        else:
            resposta_gerada = (
                "Olá! 🔮 Quem você deseja que faça sua leitura espiritual?\n"
                "Responda com:\n"
                "1️⃣ Pai Oswaldo\n"
                "2️⃣ Dona Margareth"
            )
        print(f"Mensagem para {numero_cliente}: {resposta_gerada}")
        return jsonify({"status": "success"}), 200

    # Se excedeu o número de perguntas
    if numero_cliente not in perguntas_clientes:
        perguntas_clientes[numero_cliente] = 0

    if perguntas_clientes[numero_cliente] >= limite_perguntas:
        resposta_gerada = (
            "🔮 Gratidão pela sua jornada até aqui!\n\n"
            "Todas as perguntas do seu pacote foram respondidas. "
            "Mas os mistérios do seu destino ainda reservam grandes revelações...\n\n"
            "✨ Para continuar sua leitura espiritual, adquira um novo pacote especial:\n"
            "➡️ 3 perguntas por R$ 9,90\n"
            "➡️ 5 perguntas por R$ 14,90\n\n"
            "Clique aqui e receba novas respostas do universo: [link de pagamento]"
        )
    else:
        # Gera resposta com base no cartomante escolhido
        cartomante_escolhido = cartomantes_clientes.get(numero_cliente, "Pai Oswaldo")
        resposta_gerada = gerar_resposta_ia(mensagem_usuario, cartomante_escolhido, nome_cliente, data_nascimento_cliente)

        # Incrementa o contador de perguntas
        perguntas_clientes[numero_cliente] += 1

    # Simula envio da resposta
    print(f"Mensagem para {numero_cliente}: {resposta_gerada}")

    return jsonify({"status": "success"}), 200

# Rodando o app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
