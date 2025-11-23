EcoBazaar X – Chatbot & Recommendation System (Python + Flask + Backend API Integration)
Overview

The EcoBazaar X Chatbot is a fully API-driven conversational assistant built using Python, Flask, and a lightweight NLP + fuzzy-matching system.
It connects directly with the EcoBazaar X Spring Boot Backend (http://localhost:9091
) to perform real e-commerce operations such as:

Cart operations (add, remove, show, clear)

Checkout and order creation

Order tracking & cancellation

Product search via backend

Eco-friendly recommendations

Fuzzy matching for user-friendly interaction

This service functions as an independent microservice and will integrate into the React front-end as a chatbot widget.

Technology Stack
Backend Chatbot Microservice

Python 3.10+

Flask (API framework)

Flask-CORS (Cross-origin access)

Requests (HTTP client for backend APIs)

RapidFuzz (fuzzy matching)

Pandas (for eco-recommendation engine)

Recommender System (custom ML-lite similarity engine)

Interconnected System

Spring Boot Backend API (http://localhost:9091
)

React Frontend (for actual chatbot UI)

Folder Structure
EcoChatBot/
├── app.py                        # Flask server entry point
├── chatbot_logic.py              # Core chatbot engine (+ intents + API integration)
├── requirements.txt              # Python dependencies
│
├── backend_client/               # Backend API layer
│   └── api_client.py
│
├── recommender/                  # Eco-friendly recommendation system
│   ├── recommender.py
│   └── products.csv (optional)
│
├── data/                         # ML or helper dataset storage
│   └── products.csv (if needed)
│
└── README.md                     # Project documentation

Backend API Endpoints Connected by Chatbot
Public Endpoints

GET /api/v1/products/search

GET /api/v1/products/{id}

POST /api/v1/auth/login

Customer Endpoints

GET /api/v1/cart

POST /api/v1/cart/add

DELETE /api/v1/cart/remove/{id}

POST /api/v1/checkout

GET /api/v1/profile/orders

POST /api/v1/profile/orders/{id}/cancel

The chatbot relies entirely on backend APIs—no local DB or file storage.

Key Features
1. Authentication & JWT Handling

JWT passed from frontend → chatbot → backend

Chatbot does NOT handle login UI

Frontend sends:

{
  "message": "show my cart",
  "user_id": "customer1",
  "jwt": "<token>"
}

2. Intelligent Cart System

Add items by name or fuzzy names

Remove specific items via fuzzy matching

View cart summary

Auto-suggest related products

Clear entire cart

3. Order Management

Checkout

Apply coupon (mocked)

Confirm order

Track latest order

Cancel order

4. NLP + Intent Detection

Recognizes 20+ natural-language patterns:

“add book to cart”

“show my cart”

“checkout”

“cancel my order”

“recommend eco-friendly products”

5. Eco Recommendation Engine

A CSV-powered recommender supporting:

Similar product recommendations

Carbon emission insights

Comparison queries

Running the Application
Step 1 — Install dependencies
pip install -r requirements.txt

Step 2 — Set backend base URL
$env:BACKEND_BASE_URL="http://localhost:9091"

Step 3 — Start chatbot
python app.py


Chatbot server runs at:

http://127.0.0.1:5000/chat

Chatbot API Usage
Endpoint:
POST /chat

Request Body Example
{
  "message": "add atomic habits to my cart",
  "user_id": "customer1",
  "jwt": "<YOUR_JWT>"
}

Response Example
{
  "reply": "Atomic Habits added to your cart for ₹499 x 1! You might also like Reusable Bag 🌱",
  "status": "success"
}


Technologies Used

Python (Flask) — REST microservice

Flask-CORS — cross-origin requests

Requests — backend API calling

RapidFuzz — fuzzy matching

Pandas — recommendation engine

Recommender System — ML-lite product matching

JWT Authentication

Spring Boot (Backend)

React (Frontend)