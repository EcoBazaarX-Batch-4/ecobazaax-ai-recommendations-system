import requests

API_URL = "http://127.0.0.1:5000/chat"

print("EcoBazaarX Chatbot (type 'exit' to quit)")

while True:
    msg = input("You: ").strip()
    if msg.lower() in ("exit", "quit"):
        print("Bot: Goodbye 👋 Stay eco-friendly!")
        break

    try:
        res = requests.post(API_URL, json={"message": msg})
        data = res.json()
        print("Bot:", data.get("reply"))
    except Exception as e:
        print("❌ Error connecting to bot:", e)
