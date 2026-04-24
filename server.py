from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(__name__)
# CORS-ты барлық домендерге рұқсат беретіндей етіп баптау
CORS(app, resources={r"/*": {"origins": "*"}})

# 1. API кілтін Environment Variables бөлімінен алады
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("ҚАТЕ: API кілті табылмады!")

# Сіз сұраған ең жаңа және жылдам модель (Gemini 2.0 Flash)
# Ескерту: 2.5 нұсқасы ресми шыққан соң осы жерді ғана өзгертесіз
model = genai.GenerativeModel('gemini-2.0-flash')

@app.route('/api/tests', methods=['GET'])
def generate_tests():
    topic = request.args.get('topic')
    
    if not topic:
        return jsonify({"error": "Тақырыпты көрсетіңіз"}), 400

    prompt = f"""
    Сен кәсіби оқытушысың. Пайдаланушы "{topic}" тақырыбы бойынша тест тапсырғысы келеді.
    Дәл 10 тест сұрағын құрастыр. 4 жауап нұсқасы, біреуі дұрыс.
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
        # Модельге сұраныс жіберу
        response = model.generate_content(prompt)
        
        # Жауапты тазалау (артық белгілерді алып тастау)
        content = response.text.strip()
        if content.startswith('```json'):
            content = content[7:-3]
        elif content.startswith('```'):
            content = content[3:-3]
            
        tests_data = json.loads(content)
        return jsonify(tests_data)
        
    except Exception as e:
        print(f"Генерация қатесі: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Портқа автоматты бейімделу (Railway және Render үшін)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
