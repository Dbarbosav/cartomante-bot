from flask import Flask, request, jsonify
import requests
import openai
import pytz
from datetime import datetime
import os
import random

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

limite_perguntas = 3
perguntas_clientes = {}
cartomantes_clientes = {}
perguntas_gratis_clientes = {}
coleta_dados_mapa = {}

def enviar_mensagem(numero, mensagem):
    instancia_id = "instance116881"
    token = "9k3jgki7mpfbq3j9"
    url = f"https://api.ultramsg.com/{instancia_id}/messages/chat"

    payload = {
        "token": token,
        "to": numero,
        "body": mensagem
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(url, data=payload, headers=headers)
    print(f"Resposta do envio: {response.text}")

bordoes_pai_oswaldo = [
    "Meu filho, o destino é claro para aqueles que têm coragem.",
    "Vejo que a sua jornada exige fé e ação imediata.",
    "O Universo fala contigo hoje, e eu sou apenas o mensageiro.",
    "Tudo que nasce sob a força dos ventos, floresce com o tempo certo.",
    "Não tema o que vem. Tema o que você deixa de viver."
]

bordoes_dona_margareth = [
    "Minha flor, o universo guarda doces surpresas para o seu coração.",
    "Sinto uma energia linda ao seu redor... confie nos seus instintos.",
    "Nem todo obstáculo é para te parar. Alguns são para te fortalecer.",
    "A luz que você procura está dentro de você, meu amor.",
    "Os ventos do destino estão soprando a seu favor. Permita-se florescer."
]

mantras = [
    "✨ Feche os olhos, respire fundo e repita mentalmente:\n\"Eu abro meu coração para as mensagens do Universo. Que a verdade se revele com amor e sabedoria.\"",
    "✨ Mentalize com fé:\n\"Que meus caminhos sejam iluminados pela força da fé e da esperança.\"",
    "✨ Eleve seu pensamento:\n\"Invoco a luz divina para guiar minha jornada e revelar o que preciso saber.\"",
    "✨ Sintonize sua energia:\n\"Recebo com gratidão as mensagens que o destino reservou para mim.\""
]

menu_pacotes = (
    "🔮 *Escolha seu novo pacote espiritual:*\n"
    "3 Perguntas - R$ 7,99\n"
    "5 Perguntas - R$ 9,99\n"
    "Mapa Astral - R$ 14,99\n"
    "Tiragem Especial + Análise - R$ 14,99\n\n"
    "Envie o nome do pacote que deseja."
)

def gerar_resposta_ia(prompt_usuario):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é um cartomante espiritual que responde com profundidade e empatia."},
            {"role": "user", "content": prompt_usuario}
        ],
        max_tokens=500,
        temperature=0.8,
    )
    return response['choices'][0]['message']['content'].strip()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if not data or 'data' not in data or 'body' not in data['data']:
        print("🔔 Webhook recebido mas sem 'data' ou 'body'. Ignorado.")
        return jsonify({"status": "ignored"}), 200

    mensagem_usuario = data['data']['body'].strip()
    numero_cliente = data['data']['from']
    nome_cliente = data['data'].get('senderName', 'Cliente')

    if numero_cliente not in cartomantes_clientes:
        if mensagem_usuario in ["1", "Pai Oswaldo"]:
            cartomantes_clientes[numero_cliente] = "Pai Oswaldo"
            resposta_gerada = f"✨ Seja muito bem-vindo(a)! Escolheu Pai Oswaldo. Você tem direito a 1 pergunta gratuita. Faça sua pergunta agora!"
        elif mensagem_usuario in ["2", "Dona Margareth"]:
            cartomantes_clientes[numero_cliente] = "Dona Margareth"
            resposta_gerada = f"✨ Seja muito bem-vindo(a)! Escolheu Dona Margareth. Você tem direito a 1 pergunta gratuita. Faça sua pergunta agora!"
        else:
            resposta_gerada = (
                "✨ Seja muito bem-vindo(a) à nossa jornada espiritual!\n\n"
                "Aqui, sua alma será guiada com sabedoria e carinho.\n"
                "Antes de começarmos, escolha quem irá conduzir suas mensagens:\n\n"
                "1⃣ Pai Oswaldo - Sabedoria firme e direta\n"
                "2⃣ Dona Margareth - Acolhimento e luz espiritual\n\n"
                "Responda com o número ou o nome do seu cartomante escolhido. 🔮"
            )
        enviar_mensagem(numero_cliente, resposta_gerada)
        return jsonify({"status": "success"}), 200

    if numero_cliente in coleta_dados_mapa:
        etapa = coleta_dados_mapa[numero_cliente]['etapa']
        if etapa == 'nome':
            coleta_dados_mapa[numero_cliente]['nome'] = mensagem_usuario
            coleta_dados_mapa[numero_cliente]['etapa'] = 'data'
            resposta_gerada = "Informe sua data de nascimento (DD/MM/AAAA):"
        elif etapa == 'data':
            coleta_dados_mapa[numero_cliente]['data'] = mensagem_usuario
            coleta_dados_mapa[numero_cliente]['etapa'] = 'hora'
            resposta_gerada = "Informe seu horário de nascimento (ou diga 'não sei'):"
        elif etapa == 'hora':
            coleta_dados_mapa[numero_cliente]['hora'] = mensagem_usuario
            coleta_dados_mapa[numero_cliente]['etapa'] = 'cidade'
            resposta_gerada = "Informe a cidade onde você nasceu:"
        elif etapa == 'cidade':
            coleta_dados_mapa[numero_cliente]['cidade'] = mensagem_usuario
            dados = coleta_dados_mapa.pop(numero_cliente)
            prompt_mapa = f"Gere um Mapa Astral interpretativo para:\nNome: {dados['nome']}\nData: {dados['data']}\nHora: {dados['hora']}\nCidade: {dados['cidade']}"
            resposta_gerada = gerar_resposta_ia(prompt_mapa)

        enviar_mensagem(numero_cliente, resposta_gerada)
        return jsonify({"status": "success"}), 200

    if perguntas_gratis_clientes.get(numero_cliente, 0) < 1:
        perguntas_gratis_clientes[numero_cliente] = 1
        cartomante_escolhido = cartomantes_clientes.get(numero_cliente, "Pai Oswaldo")
        mantra = random.choice(mantras)
        resposta_ia = gerar_resposta_ia(mensagem_usuario)
        bordao = random.choice(bordoes_pai_oswaldo if cartomante_escolhido == "Pai Oswaldo" else bordoes_dona_margareth)
        resposta_gerada = f"{mantra}\n\n🔮 Sua resposta:\n{resposta_ia}\n\n✨ {bordao}"
    else:
        if mensagem_usuario.lower() == "mapa astral":
            coleta_dados_mapa[numero_cliente] = {'etapa': 'nome'}
            resposta_gerada = ("🌟 Para realizar sua leitura do Mapa Astral, preciso de algumas informações:\n"
                               "1⃣ Seu nome completo\n2⃣ Sua data de nascimento\n3⃣ Seu horário de nascimento (se souber)\n4⃣ Cidade onde nasceu")
        elif mensagem_usuario.lower() == "tiragem especial":
            prompt_analise = "Realize uma tiragem especial de cartas + análise da personalidade espiritual do cliente."
            resposta_gerada = gerar_resposta_ia(prompt_analise)
        else:
            resposta_gerada = menu_pacotes

    enviar_mensagem(numero_cliente, resposta_gerada)
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
