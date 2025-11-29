EcoBazaarX – Chatbot Microservice

Python + Flask + Full Backend API Integration + NLP/Intent Engine + Recommendation System

Overview
The EcoBazaarX Chatbot is a fully API-driven conversational microservice built with Python, Flask, and a rule-based NLP engine.
It integrates tightly with the EcoBazaarX Spring Boot Backend (http://localhost:9091) and provides natural-language control over core e-commerce flows.

The chatbot performs real backend operations such as:

Core Functionalities
Add / remove items to cart (via fuzzy matching)
Show cart, clear cart
Checkout & apply coupons
Confirm order
Track order status
Cancel order
Search products via backend API
Eco-friendly product recommendations
Compare eco-impact of items
JWT-authenticated operations
Fully reactive intention engine

New Chatbot V2 Features (2025 Release)
Eco Rank Inquiry (uses /api/v1/profile/me)
Carbon Impact Inquiry (uses /api/v1/insights/profile)
Eco Education Intents
(“What is carbon footprint?”, “How is emission calculated?”)
Budget Recommendations Under ₹500
Improved fuzzy matching + fallback search
Consistent JSON responses for frontend integration
This chatbot runs as an independent microservice and plugs directly into the React frontend widget.

Technology Stack
Chatbot Microservice
Python 3.10+
Flask (REST API)
Flask-CORS
Requests (Backend API Caller)
RapidFuzz (Fuzzy Matching)
Pandas (Recommender Engine)
Custom NLP + Intent Engine

Interconnected System
Spring Boot Backend (Main APIs)
React Frontend (Chat UI widget)
Python Microservice (Chat Engine)

Project Structure
EcoChatBot/
├── app.py                        # Flask server entry point
├── chatbot_logic.py              # Core chatbot engine (+ intents + API integration)
├── requirements.txt              # Python dependencies
│
├── backend_client/
│   └── api_client.py             # (optional abstraction layer)
│
├── recommender/
│   ├── recommender.py
│   └── products.csv              # dataset (optional)
│
├── data/
│   └── products.csv              # example ML dataset
│
└── README.md

Backend Endpoints Used by Chatbot
Public
GET /api/v1/products
GET /api/v1/products/search?q=...
GET /api/v1/products/{id}
POST /api/v1/auth/login

Customer (Requires JWT)
GET /api/v1/cart
POST /api/v1/cart/add
DELETE /api/v1/cart/remove/{id}
POST /api/v1/checkout
GET /api/v1/profile/orders
POST /api/v1/profile/orders/{id}/cancel
GET /api/v1/profile/me (Eco Rank)
GET /api/v1/insights/profile (Carbon Impact)
The chatbot does not use any local database — all data is synced with backend.

Key Features
1. JWT Authentication
The frontend sends JWT with each request:

{
  "message": "show my cart",
  "user_id": "customer1",
  "jwt": "<token>"
}

2. Intelligent Cart System
Add items by name:
"add bamboo bottle to my cart"
Fuzzy matching for user misspellings
"add bambu botel"
Remove specific items
View full cart summary
Auto-suggest related items
Clear cart in one command

3. Order Management
Checkout
Apply coupons (simulated)
Confirm orders
Track delivery
Cancel orders

4. Advanced Intent Detection
Supports 30+ natural phrasing patterns:
"add 2 books to cart"
"show basket"
"checkout"
"cancel my order"
"suggest eco-friendly alternatives"
"product under 500"
"what is carbon footprint"

5. Eco Recommendation Engine
CSV-based similarity matching
Uses carbon footprint comparison
Supports comparison queries
Eco-friendly alternatives
Budget filtering

6. New Eco Intelligence
Eco Rank → “What is my eco rank?”
Carbon Saved → “How much carbon have I saved?”
Eco Education
“What is carbon footprint?”
“How is emission calculated?”

Installing & Running the Chatbot
Step 1 — Install Dependencies
pip install -r requirements.txt

Step 2 — Set Backend URL
PowerShell:
$env:BACKEND_BASE_URL="http://localhost:9091"

or Linux/macOS:
export BACKEND_BASE_URL=http://localhost:9091

Step 3 — Start Chatbot
python app.py

Chatbot endpoint:
POST http://127.0.0.1:5000/chat

Usage (Frontend or Postman)
Request
POST /chat
{
  "message": "add atomic habits to my cart",
  "user_id": "customer1",
  "jwt": "<JWT>"
}

Response
{
  "reply": "Atomic Habits added to your cart for ₹499 x 1! 🛒 You might also like Reusable Bag 🌱",
  "status": "success"
}

Supported Chatbot Commands
1. Cart
“add atomic habits to my cart”
“show my cart”
“remove bottle from cart”
“clear my cart”

2. Orders
“checkout”
“apply SAVE15”
“confirm order”
“track my order”
“cancel order”

3. Eco Features
“what is my eco rank”
“how much carbon have I saved”
“what is carbon footprint”
“how is emission calculated”

4. Recommendations
“recommend an eco friendly bottle”
“compare bamboo vs plastic bottle”
“suggest something under 500”

Chatbot API (Flask)
Endpoint
POST /chat

JSON Contract
Required fields:
message
optional: jwt, user_id

Developers & Maintenance
Built as a microservice for EcoBazaarX
Easy to extend (intents & handlers modularized)
Fully compatible with React frontend integration
All shopping logic executed via backend APIs

License
Internal project — EcoBazaarX (2025)
