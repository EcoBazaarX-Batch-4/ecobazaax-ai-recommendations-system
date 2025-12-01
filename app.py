from flask import Flask, request, jsonify
from flask_cors import CORS
import chatbot_logic

app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    user_id = data.get('user_id', 'guest')
    token = data.get('jwt_token')

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    # FIX: Changed 'process_message' to 'chatbot_response' to match chatbot_logic.py
    response_text = chatbot_logic.chatbot_response(user_message, user_id=user_id, jwt_token=token)
    
    return jsonify({"response": response_text})

if __name__ == '__main__':
    app.run(port=5000, debug=True)