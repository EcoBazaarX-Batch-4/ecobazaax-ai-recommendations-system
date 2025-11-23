import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import chatbot logic (FULL API MODE)
from chatbot_logic import chatbot_response

# Optional recommender (if needed)
from recommender.recommender import Recommender

# -----------------------------------------------------
# Flask Setup
# -----------------------------------------------------
app = Flask(__name__)
app.secret_key = "eco_chatbot_secret_key"
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EcoChatBot")

recommender = Recommender()

# -----------------------------------------------------
# Root
# -----------------------------------------------------
@app.route("/")
def home():
    return jsonify({
        "message": "EcoBazaarX Chatbot API is running",
        "note": "Send POST /chat with message + user_id + optional JWT"
    })

# -----------------------------------------------------
# CHAT ENDPOINT
# -----------------------------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True, silent=True) or {}
        message = (data.get("message") or "").strip()
        user_id = data.get("user_id", "guest")

        # Get JWT from either:
        # 1) Authorization header, or
        # 2) JSON body {jwt: "..."}
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            jwt_token = auth_header.replace("Bearer ", "").strip()
        else:
            jwt_token = data.get("jwt")

        if not message:
            return jsonify({"reply": "Message cannot be empty.", "status": "error"})

        # Call chatbot
        bot_reply = chatbot_response(
            user_input=message,
            user_id=user_id,
            jwt_token=jwt_token
        )

        return jsonify({
            "reply": bot_reply,
            "status": "success"
        })

    except Exception as e:
        logger.exception("Chat error")
        return jsonify({
            "reply": "Server error occurred.",
            "status": "error",
            "error": str(e)
        }), 500


# -----------------------------------------------------
# Start App
# -----------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
