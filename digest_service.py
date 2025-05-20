from flask import Flask, request, jsonify
import requests
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LLM_API_AUTH_USER = os.getenv("LLM_API_AUTH_USER")
LLM_API_AUTH_PASS = os.getenv("LLM_API_AUTH_PASS")
PROMPT = os.getenv("PROMPT")
INSTRUCTIONS = os.getenv("INSTRUCTIONS")
MODEL = os.getenv("MODEL")

app = Flask(__name__)

@app.route('/', methods=['POST'])
def generate_digest():
    logger.info("Пришел запрос на создание дайджеста")
    data = request.get_json()
    if not data or "documents" not in data:
        return jsonify({"error": "Неверный формат запроса"}), 400

    documents = data["documents"]

    # Собираем тексты новостей, разделяя их несколькими переносами строки
    prompt = PROMPT
    prompt += "\n\n".join(doc.get("text", "") for doc in documents)
    prompt += "\n\n\n" + INSTRUCTIONS

    # Если итоговый промпт слишком длинный, используем summary вместо text
    if len(prompt) > 90000:
        prompt = "\n\n".join(doc.get("summary", "") for doc in documents)

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(
        "http://ai.nt.fyi/api/generate",
        json=payload,
        auth=(LLM_API_AUTH_USER, LLM_API_AUTH_PASS)
    )

    if response.status_code != 200:
        return jsonify({
            "error": "Ошибка при вызове LLM API",
            "details": response.text
        }), response.status_code

    # Возвращаем результат работы модели как ответ на исходный POST запрос
    logger.info("Дайджест отправляется на бекенд")
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
