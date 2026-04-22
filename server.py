from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import json
import os

app = Flask(__name__)
# Бұл өте маңызды! Timeweb-тегі сайтың Render-ге сұраныс жібере алуы үшін керек:
CORS(app) 

# 1. API кілтін Render-дің баптауларынан (Environment Variables) аламыз
API_KEY = os.environ.get("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("ҚАТЕ: API кілті табылмады!")

# Сенің тізіміңдегі ең жаңа модель
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/api/tests', methods=['GET'])
def generate_tests():
    topic = request.args.get('topic')
    
    if not topic:
        return jsonify({"error": "Тақырыпты көрсетіңіз"}), 400

    prompt = f"""
    Сен кәсіби оқытушысың. Пайдаланушы "{topic}" тақырыбы бойынша тест тапсырғысы келеді.
    Дәл 20 тест сұрағын құрастыр. 4 жауап нұсқасы, біреуі дұрыс.
    Әр сұраққа неге бұл жауап дұрыс екенін түсіндіретін қысқаша түсініктеме (explanation) жаз.
    Жауапты JSON форматында қайтар: массив объектілер. Қосымша мәтінсіз.
    Тіл: Қазақ тілі.
    [
      {{
          "question": "сұрақ",
          "options": ["1", "2", "3", "4"],
          "correctAnswer": "дұрыс",
          "explanation": "түсіндірме"
      }}
    ]
    """

    try:
        response = model.generate_content(prompt)
        # ИИ-дің жауабын тазалау
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        tests_data = json.loads(clean_text)
        return jsonify(tests_data)
        
    except Exception as e:
        print(f"Қате: {e}")
        return jsonify({"error": "Генерация сәтсіз аяқталды"}), 500

if __name__ == '__main__':
    # 2. Render-дің портына бейімделу (бұл жер өзгерді)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
