from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.utils.ai_utils import MODEL_NAME
import google.generativeai as genai

chatbot = Blueprint('chatbot', __name__)

@chatbot.route('/chat', methods=['POST'])
@login_required
def chat():
    try:
        data = request.get_json()
        user_input = data.get('message', '')
        
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(user_input)
        
        return jsonify({
            'success': True,
            'response': response.text
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500