from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import google.generativeai as genai
from app.utils.ai_utils import setup_gemini, get_valid_model

chatbot = Blueprint("chatbot", __name__)


@chatbot.route("/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json() or {}
    user_input = data.get("message", "")

    # Try to configure and pick a model at runtime. If not available,
    # provide a graceful fallback response so the server still runs.
    try:
        configured = setup_gemini()
        model_name = get_valid_model() if configured else None

        if not model_name:
            # Fallback: echo or provide helpful info when AI is not configured
            return jsonify({
                "success": True,
                "response": "AI not configured. Set API_KEY to enable chatbot.",
            })

        model = genai.GenerativeModel(model_name)
        # Use the appropriate API for your genai client; this is an example
        response = model.generate_content(user_input)

        return jsonify({"success": True, "response": getattr(response, "text", str(response))})
    except Exception as e:
        current_app.logger.exception("Chatbot error")
        return jsonify({"success": False, "error": str(e)}), 500