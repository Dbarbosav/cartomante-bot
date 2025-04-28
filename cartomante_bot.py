from flask import Flask, request, jsonify
import requests
import openai
import pytz
from datetime import datetime
import os
import random

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

WPP_SERVER_URL = os.getenv("WPP_SERVER_URL")
SESSION = os.getenv("WPP_SESSION_NAME", "cartomante-pro")

limite_perguntas = 3
perguntas_clientes = {}
cartomantes_clientes = {}
perguntas_gratis_clientes = {}
coleta_dados_mapa = {}

def enviar_mensagem(numero, mensagem):
    url = f"{WPP_SERVER_URL}/api/send-message"
    payload = {
        "session": SESSION,
        "phone": numero,
        "text": mensagem
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Resposta envio: {response.text}")
    except Exception as e:
        print(f"Erro no envio: {e}")

# (Manter o restante do código original do bot, conforme sua última versão completa)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
