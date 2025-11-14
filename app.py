import logging
from flask import Flask, request, jsonify, session
from flask_cors import CORS

# 🧠 Import chatbot logic and cart helpers
from chatbot_logic import (
    chatbot_response,
    get_cart_items,
    get_cart_total,
    session_memory
)

# 🌱 Import upgraded Recommender
from recommender.recommender import Recommender

# -----------------------------------------------------
# 🌍 Flask Setup
# -----------------------------------------------------
app = Flask(__name__)
app.secret_key = "eco_chatbot_secret_key"
CORS(app)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EcoChatBot")

# Initialize recommender once when server starts
recommender = Recommender()

# -----------------------------------------------------
# 🏠 Root Route
# -----------------------------------------------------
@app.route("/")
def home():
    return jsonify({
        "message": "🌿 EcoBazaarX Chatbot API is active!",
        "endpoints": {
            "POST /chat": "Send JSON { 'message': 'recommend an eco brush', 'user_id': 'user123' }"
        }
    })

# -----------------------------------------------------
# 💬 Chat Route
# -----------------------------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    """
    Handles user input and returns chatbot or recommender responses.
    Expected JSON:
    {
        "message": "recommend an eco brush",
        "user_id": "user123"
    }
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        user_input = (data.get("message") or "").strip()
        user_id = data.get("user_id", "guest_user")

        if not user_input:
            return jsonify({"reply": "Message cannot be empty.", "status": "error"}), 400

        session["user_id"] = user_id

        lower_input = user_input.lower()

        # -----------------------------------------------------
        # 🌱 STEP 1: Detect Recommendation or Comparison Intent
        # -----------------------------------------------------
        rec_keywords = ["recommend", "suggest", "eco friendly", "eco-friendly", "compare"]
        if any(word in lower_input for word in rec_keywords):
            result = recommender.recommend(user_input)
            logger.info("Recommender input: %s", user_input)

            # ✅ Successful recommendation or comparison
            if result.get("success"):
                product = result["recommended"]
                reason = result["reason"]

                # Friendly chatbot-style reply
                bot_reply = f"🌿 I recommend **{product['name']}** — {reason}"
                return jsonify({
                    "reply": bot_reply,
                    "parsed": result.get("parsed", {}),
                    "cart": get_cart_items(user_id),
                    "total": get_cart_total(user_id),
                    "status": "success"
                })

            # ⚠️ If recommender fails (no match found)
            bot_reply = result.get("message", "Sorry, I couldn’t find a suitable eco product.")
            return jsonify({
                "reply": bot_reply,
                "parsed": result.get("parsed", {}),
                "cart": get_cart_items(user_id),
                "total": get_cart_total(user_id),
                "status": "success"
            })

        # -----------------------------------------------------
        # 💬 STEP 2: Fallback to Normal Chatbot Flow
        # -----------------------------------------------------
        bot_reply = chatbot_response(user_input, user_id)

        response_payload = {
            "reply": bot_reply,
            "cart": get_cart_items(user_id),
            "total": get_cart_total(user_id),
            "status": "success"
        }

        # If chatbot generated order info, include it
        last_order = session_memory.get("last_order") or {}
        if "order_id" in last_order:
            response_payload["order_id"] = last_order["order_id"]

        logger.info("User(%s): %s", user_id, user_input)
        logger.info("Bot reply: %s", bot_reply)
        return jsonify(response_payload)

    except Exception as e:
        logger.exception("❌ Error processing /chat request")
        return jsonify({
            "reply": "⚠️ Server error occurred. Please try again.",
            "status": "error",
            "error": str(e)
        }), 500

# -----------------------------------------------------
# 🧹 Clear Session Route
# -----------------------------------------------------
@app.route("/clear_session", methods=["POST"])
def clear_session():
    session.clear()
    return jsonify({"message": "Session cleared successfully.", "status": "success"})

@app.route("/save_session", methods=["POST"])
def save_session_route():
    from chatbot_logic import save_session_data
    save_session_data()
    return jsonify({"message": "Session data saved manually.", "status": "success"})


# -----------------------------------------------------
# 🚀 Run App
# -----------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
