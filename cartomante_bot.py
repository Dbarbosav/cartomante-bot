import random
import logging
import requests
from flask import Flask, request, jsonify
from datetime import datetime
import pytz

app = Flask(__name__)

# Configuração de logging
logging.basicConfig(
    filename='historico_consultas.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

historico_cache = []

# Banco dos Arcanos Maiores com emojis para energia
cartas_tarot = [
    # cartas já adicionadas anteriormente...
]

def tirar_cartas(qtd=1):
    return random.sample(cartas_tarot, qtd)

def formatar_interpretacao(cartas, pergunta):
    mensagens = []
    for idx, carta in enumerate(cartas):
        tema = ""
        if idx == 0:
            tema = "Passado"
        elif idx == 1:
            tema = "Presente"
        elif idx == 2:
            tema = "Futuro"
        energia_emoji = "🌟" if carta['energia'] == 'positiva' else ("⚖️" if carta['energia'] == 'neutra' else "⚡")
        mensagens.append(f"{tema}: {energia_emoji} *{carta['nome']}* - {carta['significado']}")
    return f"🔮 Tiragem para a pergunta: '{pergunta}'\n" + "\n".join(mensagens)

@app.route('/webhook', methods=['POST'])
def webhook():
    if not request.is_json:
        return jsonify({"erro": "Requisição deve ser JSON"}), 400

    dados = request.get_json()
    numero = dados.get('numero')
    pergunta = dados.get('mensagem', '').lower()

    if not pergunta.strip():
        return jsonify({"erro": "Mensagem inválida ou vazia."}), 400

    if "ajuda" in pergunta:
        ajuda_msg = ("🔮 Bem-vindo à sua consulta mística!\n"
                     "Envie uma pergunta como:\n"
                     "- 'tiragem completa' (3 cartas: passado, presente, futuro)\n"
                     "- 'tiragem amor', 'tiragem trabalho', 'tiragem saúde'\n"
                     "- Ou qualquer pergunta livre ✨")
        return jsonify({"status": "ok", "mensagem": ajuda_msg})

    if any(t in pergunta for t in ["tiragem completa", "tiragem amor", "tiragem trabalho", "tiragem saúde"]):
        cartas = tirar_cartas(3)
    else:
        cartas = tirar_cartas(1)

    interpretacao = formatar_interpretacao(cartas, pergunta)
    imagens = [carta['imagem'] for carta in cartas]

    fuso_brasilia = pytz.timezone('America/Sao_Paulo')
    timestamp = datetime.now(fuso_brasilia).isoformat()

    resposta = {
        "status": "ok",
        "timestamp": timestamp,
        "numero": numero,
        "mensagem": interpretacao,
        "imagens": imagens
    }

    historico_cache.append({
        "numero": numero,
        "pergunta": pergunta,
        "cartas": [carta['nome'] for carta in cartas],
        "data": timestamp
    })
    if len(historico_cache) > 100:
        historico_cache.pop(0)

    return jsonify(resposta)

@app.route('/historico', methods=['GET'])
def historico():
    return jsonify({"status": "ok", "historico": historico_cache})

if __name__ == '__main__':
    import sys
    if "teste" in sys.argv:
        print("Rodando em modo teste!")
    else:
        app.run(host='0.0.0.0', port=5000)
