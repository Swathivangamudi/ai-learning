from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import pytesseract
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

# Set your OpenAI API key here
OPENAI_API_KEY = 'AIzaSyDt3A2o3AgDclNg9MgMgdcsKVTCZ0Rp96I'

@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')

    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json',
        },
        json={
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'user', 'content': question}],
        }
    )

    answer = response.json().get('choices')[0].get('message').get('content')
    return jsonify(answer)

@app.route('/api/ocr', methods=['POST'])
def ocr():
    file = request.files['image']
    image = Image.open(io.BytesIO(file.read()))
    text = pytesseract.image_to_string(image)
    return jsonify({'text': text})

if __name__ == '__main__':
    app.run(debug=True)