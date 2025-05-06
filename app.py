from flask import Flask, request, jsonify
import requests
import os
from openai import OpenAI

app = Flask(__name__)

# Pegando as variáveis de ambiente
WHAPI_TOKEN = os.getenv('WHAPI_TOKEN')
WHAPI_URL = os.getenv('WHAPI_URL', 'https://gate.whapi.cloud')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

def send_whatsapp_message(to_number, message):
    url = f"{WHAPI_URL}/messages/text"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WHAPI_TOKEN}'
    }
    payload = {
        'to': to_number,
        'type': 'text',
        'text': {
            'body': message
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f'Resposta Whapi: {response.status_code} {response.text}')
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

@app.route('/webhook', methods=['POST'])  # 🔥 Corrigido aqui
def webhook():
    data = request.json
    print(f"Recebido: {data}")

    if 'messages' in data:
        for message_data in data['messages']:
            from_number = message_data.get('from')
            user_message = message_data.get('text', {}).get('body')

            if not user_message:
                print("Mensagem recebida sem corpo de texto.")
                continue

            # Prompt personalizado para Cartomante
            prompt = (
                f"Você é um cartomante espiritualista. Aja como se fosse o Pai Oswaldo ou Dona Margareth, "
                f"respondendo de forma mística, acolhedora e detalhada sobre a dúvida: '{user_message}'. "
                f"Inclua também reflexões e conselhos espirituais."
            )

            try:
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Você é um cartomante profissional."},
                        {"role": "user", "content": prompt}
                    ]
                )
                response_text = completion.choices[0].message.content.strip()

            except Exception as e:
                print(f"Erro OpenAI: {e}")
                response_text = "Desculpe, tivemos um problema ao consultar os espíritos agora. Tente novamente mais tarde."

            # Envia a resposta
            send_whatsapp_message(from_number, response_text)

    return jsonify({'status': 'mensagem recebida'})

if __name__ == '__main__':
    app.run(port=5000)
