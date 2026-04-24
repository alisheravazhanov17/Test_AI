import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

# Render-дегі Environment Variables-тен кілтті алады
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/generate', methods=['GET'])
def generate_tests():
    topic = request.args.get('topic')
    if not topic:
        return jsonify({"error": "Тақырыпты жазыңыз"}), 400

    try:
        # Groq-қа сұраныс жіберу
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Сен кәсіби тест құрастырушысың. Пайдаланушы берген тақырып бойынша 10 сұрақтан тұратын тестті тек JSON форматында қайтар. Формат: [{'question': '...', 'options': ['A', 'B', 'C', 'D'], 'answer': '...', 'explanation': '...'}]. Түсіндірме (explanation) міндетті түрде әр сұраққа болсын. Жауаптарды тек қазақ тілінде бер."
                },
                {
                    "role": "user",
                    "content": topic,
                }
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        # Жауапты алу және JSON ретінде қайтару
        result = json.loads(completion.choices[0].message.content)
        
        # Сұрақтар тізімін тауып алу
        if isinstance(result, dict):
            for key in result:
                if isinstance(result[key], list):
                    return jsonify(result[key])
        
        return jsonify(result)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
