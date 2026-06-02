from flask import Blueprint, render_template, request, jsonify
from app.services.ragchain import ask_question

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/')
def index():
    return render_template('index.html')

@chat_bp.route('/ask', methods=['POST'])
def ask():
    data = request.get_json(silent=True) or {}
    question = (data.get('question') or '').strip()
    filters = data.get('filters') or {}
    history = data.get('history') or []
    if not question:
        return jsonify({'error': 'No question provided.'}), 400
    result = ask_question(question, filters=filters, history=history)
    return jsonify(result)
