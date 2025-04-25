import random
import logging
import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Configuração de logging
logging.basicConfig(
    filename='historico_consultas.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

# Cache simples em memória para histórico (limite de 100 últimas entradas)
historico_cache = []

# Banco de cartas exemplo (pode ser migrado para JSON ou DB futuramente)
cartas_tarot = [
    {
        "nome": "A Estrela",
        "significado": "Esperança, inspiração e serenidade à frente.",
        "imagem": "https://exemplo.com/imagens/a_estrela.jpg"
    },
    {
        "nome": "O Louco",
        "significado": "Novos começos e fé no desconhecido.",
        "imagem": "https://exemplo.com/imagens/o_louco.jpg"
    },
    {
        "nome": "A Morte",
        "significado": "Transformação profunda e renascimento.",
        "imagem": "https://exemplo.com/imagens/a_morte.jpg"
    },
    # Adicione mais cartas aqui...
]

def tirar_carta():
    return random.choice(cartas_tarot)

def gerar_interpretacao(pergunta, carta):
    return (
        f"Ao perguntar: '{pergunta}', a carta *{carta['nome']}* revela: {carta['significado']}\n"
        f"Este é um sinal para refletir e seguir sua intuição, buscando o que acalma seu coração."
    )

@app.route('/webhook', methods=['POST'])
def webhook():
    if not request.is_json:
        return jsonify({"erro": "Requisição deve ser JSON"}), 400

    dados = request.get_json()
    numero = dados.get('numero')
    pergunta = dados.get('mensagem')

    if not isinstance(pergunta, str) or not pergunta.strip():
        return jsonify({"erro": "Mensagem inválida ou vazia."}), 400

    carta = tirar_carta()
    interpretacao = gerar_interpretacao(pergunta, carta)

    resposta = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "numero": numero,
        "mensagem": f"🔮 A carta tirada foi *{carta['nome']}*\n\n{interpretacao}",
        "imagem": carta['imagem'],
        "audio": f"https://exemplo.com/audios/{carta['nome'].lower().replace(' ', '_')}.mp3"
    }

    # Log em arquivo
    logging.info(f"Pergunta: {pergunta} | Carta: {carta['nome']} | Numero: {numero}")

    # Adiciona ao cache
    historico_cache.append({
        "numero": numero,
        "pergunta": pergunta,
        "carta": carta['nome'],
        "data": resposta['timestamp']
    })
    if len(historico_cache) > 100:
        historico_cache.pop(0)

    return jsonify(resposta)

@app.route('/historico', methods=['GET'])
def historico():
    return jsonify({"status": "ok", "historico": historico_cache})

# Função de teste local (simulação de envio de pergunta e consulta ao histórico)
def rodar_testes():
    print("\nSimulando requisição ao /webhook...")
    payload = {
        "numero": "+5511999999999",
        "mensagem": "O que me espera no amor?"
    }
    r1 = requests.post("http://127.0.0.1:5000/webhook", json=payload)
    print("Status:", r1.status_code)
    print("Resposta:", r1.json())

    print("\nConsultando histórico...")
    r2 = requests.get("http://127.0.0.1:5000/historico")
    print("Status:", r2.status_code)
    print("Histórico:", r2.json())

if __name__ == '__main__':
    import sys
    if "teste" in sys.argv:
        rodar_testes()
    else:
        app.run(host='0.0.0.0', port=5000)
