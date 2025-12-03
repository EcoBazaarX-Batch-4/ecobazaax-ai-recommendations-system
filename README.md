# 🌿 EcoBazaarX AI Recommendations System - Complete Documentation

**Version:** 2.0  
**Last Updated:** December 2, 2025  
**Status:** Production Ready

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [System Components](#system-components)
4. [Installation & Setup](#installation--setup)
5. [Configuration](#configuration)
6. [Running the Application](#running-the-application)
7. [API Endpoints](#api-endpoints)
8. [Chatbot Features](#chatbot-features)
9. [Recommender System](#recommender-system)
10. [Database Schema](#database-schema)
11. [Troubleshooting](#troubleshooting)
12. [Project Structure](#project-structure)

---

## 🎯 Project Overview

**EcoBazaarX** is a comprehensive e-commerce platform focused on sustainable and eco-friendly products. This project consists of three main components working together:

### Key Features:
- 🤖 **AI-Powered Chatbot** - Intelligent product recommendations and customer support
- 🌍 **Eco-Friendly Recommendations** - Carbon footprint analysis and product comparisons
- 🛒 **Full E-Commerce System** - Frontend, Backend, and AI integration
- 📊 **Carbon Tracking** - Real-time carbon emission monitoring for products
- 💬 **Multi-Intent NLP** - Intent detection for diverse user queries
- 🔐 **Secure Authentication** - JWT-based user authentication

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React/Vite)                   │
│                 (ecobazaax-frontend-main)                   │
│                  Port: 5173 (Dev) / 80 (Prod)              │
└─────────────────────────────────────────────────────────────┘
                              ↑
                              ↓ (HTTP Requests)
┌─────────────────────────────────────────────────────────────┐
│                CHATBOT SERVER (Flask)                       │
│            (localhost:5000 - This Repository)              │
│                                                             │
│  - Intent Detection                                         │
│  - Cart Operations                                          │
│  - Order Management                                         │
│  - User Interactions                                        │
│  - Recommender Engine (ML)                                 │
└─────────────────────────────────────────────────────────────┘
                              ↑
                              ↓ (HTTP Requests to /api/v1/*)
┌─────────────────────────────────────────────────────────────┐
│              BACKEND API (Spring Boot / Java)               │
│              (localhost:8080 - External)                    │
│                                                             │
│  - Product Queries                                          │
│  - Cart Management                                          │
│  - Order Processing                                         │
│  - User Authentication                                      │
└─────────────────────────────────────────────────────────────┘
                              ↑
                              ↓ (SQL Queries)
                   ┌─────────────────────┐
                   │  MySQL Database     │
                   │ (ecobazaarx schema) │
                   │                     │
                   │ - Products          │
                   │ - Categories        │
                   │ - Orders            │
                   │ - Users             │
                   │ - Cart Items        │
                   └─────────────────────┘
```

### Communication Flow:

```
User Interface
    ↓
Frontend (React/Vite) ← Port 5173
    ↓ (POST /chat)
Chatbot Server (Flask) ← Port 5000
    ↓ (Intent Detection & Processing)
    ├─→ Recommender Engine (ML - Local)
    │
    └─→ Backend API (Spring Boot) ← Port 8080
            ↓ (SQL Queries)
            MySQL Database
            ↓
            Response
        ↑
    Chatbot Formats & Returns Response
    ↑
Frontend Displays to User
```

### Key Points:
- ✅ **Frontend ONLY talks to Chatbot** (Port 5000)
- ✅ **Chatbot ONLY talks to Backend** (Port 8080)
- ✅ **Backend ONLY talks to Database** (MySQL)
- ✅ **Recommender Engine** runs locally in Chatbot (no direct DB access)
- ✅ **No direct Frontend-Backend communication** for chatbot flows
- ✅ **No direct Chatbot-Database access** (only through Backend API)

---

## 🔧 System Components

### 1. **AI Chatbot System** (This Repository)
- **Language:** Python 3.13.3
- **Framework:** Flask
- **Port:** 5000
- **Key Files:**
  - `app.py` - Flask application entry point
  - `chatbot_logic.py` - Core chatbot logic and intent detection
  - `recommender/recommender.py` - ML-based recommendation engine

### 2. **Frontend Application**
- **Language:** JavaScript/JSX
- **Framework:** React with Vite
- **Repository:** `ecobazaax-frontend-main`
- **Key Components:**
  - `ChatButton.jsx` - Chat interface trigger
  - `ChatModal.jsx` - Chat modal interface
  - `ProductCard.jsx` - Product display
  - Context providers for state management

### 3. **Backend API (External)**
- **Language:** Java
- **Framework:** Spring Boot
- **Port:** 8080
- **Database:** MySQL
- **Endpoints:**
  - `/api/v1/products` - Product listing
  - `/api/v1/products/search` - Product search
  - `/api/v1/cart` - Cart operations
  - `/api/v1/checkout` - Checkout process

---

## 💻 Installation & Setup

### Prerequisites
- Python 3.10+ (Tested on 3.13.3)
- pip (Python package manager)
- Virtual Environment
- MySQL Server (running and accessible)
- Backend API running on `localhost:8080`

### Step 1: Clone the Repository

```bash
git clone https://github.com/EcoBazaarX-Batch-4/ecobazaax-ai-recommendations-system-chatbot-v2.git
cd ecobazaax-ai-recommendations-system-chatbot-v2
```

### Step 2: Create Virtual Environment

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies Installed:**
- `Flask` - Web framework
- `flask-cors` - Cross-origin resource sharing
- `requests` - HTTP requests library
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `scikit-learn` - Machine learning
- `rapidfuzz` - Fuzzy string matching
- `python-dotenv` - Environment variables
- `mysql-connector-python` - MySQL connectivity

### Step 4: Verify Installation

```bash
python -c "import flask, pandas, sklearn; print('✅ All dependencies installed successfully!')"
```

---

## ⚙️ Configuration

### 1. **Environment Variables** (Optional)

Create a `.env` file in the project root:

```env
# Backend API Configuration
BACKEND_BASE_URL=http://localhost:8080

# Request Timeout (seconds)
REQUEST_TIMEOUT=6.0

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Logging
LOG_LEVEL=INFO
```

### 2. **Backend API Configuration**

Ensure your Spring Boot backend is running:
- URL: `http://localhost:8080`
- Required endpoints:
  - `GET /api/v1/products` - Returns all products
  - `GET /api/v1/products/search?q=query` - Search products
  - `GET /api/v1/cart` - Get user cart
  - `POST /api/v1/cart/add` - Add item to cart
  - `DELETE /api/v1/cart/remove/{id}` - Remove from cart
  - `POST /api/v1/checkout` - Process checkout

### 3. **Database Configuration** (Optional - Used as Fallback)

If direct database access is needed:

```python
# In recommender/recommender.py
DATABASE_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "your_password",
    "database": "ecobazaarx"
}
```

---

## 🚀 Running the Application

### Start the Chatbot Server

**Using Virtual Environment (Recommended):**

```bash
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
python app.py

# macOS/Linux
source venv/bin/activate
python app.py
```

**Output Should Show:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Verify Server is Running

**Test Endpoint:**
```bash
curl http://127.0.0.1:5000/
```

**Expected Response:**
```json
{
  "message": "EcoBazaarX Chatbot API is running",
  "note": "Send POST /chat with message + user_id + optional JWT"
}
```

### Full Stack Startup

To run the complete system:

```bash
# Terminal 1: Backend API (external - must be running)
# Ensure Spring Boot backend is running on port 8080

# Terminal 2: Frontend
cd ../ecobazaax-frontend-main
npm install
npm run dev

# Terminal 3: Chatbot (this project)
python app.py
```

---

## 🔌 API Endpoints

### 1. **Root Endpoint**

```
GET /
```

**Response:**
```json
{
  "message": "EcoBazaarX Chatbot API is running",
  "note": "Send POST /chat with message + user_id + optional JWT"
}
```

### 2. **Chat Endpoint** (Main)

```
POST /chat
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Hello, recommend an eco-friendly bottle",
  "user_id": "user123",
  "jwt": "optional_jwt_token"
}
```

**Response:**
```json
{
  "reply": "🌿 I recommend **Bamboo Water Bottle** — It's more eco-friendly with 2.5 kg CO₂e compared to Plastic Bottle (5.8 kg CO₂e).",
  "status": "success"
}
```

### 3. **Error Response**

```json
{
  "reply": "Server error occurred.",
  "status": "error",
  "error": "error_message_here"
}
```

---

## 💬 Chatbot Features

### Intent Detection

The chatbot recognizes the following intents:

| Intent | Keywords | Example | Response |
|--------|----------|---------|----------|
| `greeting` | hi, hello, hey | "Hello" | Welcome message |
| `eco_tip` | tip | "Give me a tip" | Random eco-tip |
| `cart_query` | show, see, cart | "Show my cart" | Display cart items |
| `cart_added` | add, put, cart | "Add bottle to cart" | Item added confirmation |
| `cart_remove_single` | remove, delete, from cart | "Remove item" | Item removed |
| `cart_clear` | clear, empty, cart | "Clear cart" | Cart cleared |
| `checkout` | checkout, place order | "Checkout" | Checkout process |
| `apply_coupon` | coupon, apply | "Apply SAVE15" | Coupon applied |
| `payment_method` | upi, cod, wallet | "Pay with UPI" | Payment method set |
| `confirm_order` | confirm, finalize | "Confirm order" | Order confirmation |
| `track_order` | track, delivery, status | "Track order" | Order status |
| `cancel_order` | cancel, abort, stop | "Cancel order" | Order cancellation |
| `eco_recommendation` | recommend, eco-friendly | "Recommend bottle" | Product recommendation |
| `eco_info` | carbon, emission, footprint | "Carbon footprint?" | Eco-info response |
| `eco_comparison` | compare, vs, alternative | "Compare bags" | Product comparison |

### Supported User Interactions

1. **Product Search & Recommendation**
   - Fuzzy matching for product names
   - Carbon footprint comparison
   - Eco-friendly alternatives suggestion

2. **Cart Management**
   - Add products to cart
   - View cart contents
   - Remove specific items
   - Clear entire cart
   - Real-time total calculation

3. **Order Management**
   - Checkout process
   - Coupon code application
   - Payment method selection
   - Order confirmation
   - Order tracking
   - Order cancellation

4. **Eco Education**
   - Carbon emission tips
   - Sustainability information
   - Product comparisons
   - Environmental impact metrics

---

## 🧠 Recommender System

### How It Works

1. **Data Source Priority:**
   - ✅ Primary: Backend API (`/api/v1/products`)
   - ✅ Fallback: CSV file (`product_data.csv`)
   - ✅ Fallback: Local database (if available)

2. **Matching Algorithm:**
   - **Fuzzy Matching** - Tolerates typos and partial matches
   - **Semantic Matching** - TF-IDF vectorization for meaning
   - **Category Normalization** - Handles category synonyms

3. **Ranking Criteria:**
   - Carbon footprint (ascending = better)
   - Eco-points score
   - Product ratings
   - Material sustainability
   - Price efficiency

### Product Comparison

**Example: Eco vs Non-Eco**

```
User Query: "Compare plastic bag and eco bag"

Response:
- Eco Bag: 1.2 kg CO₂e ✅
- Plastic Bag: 3.5 kg CO₂e ❌

Recommendation: "Eco Bag is 65% more eco-friendly!"
```

### Recommendation Algorithm

```python
1. Parse user input
   ├─ Extract product keywords
   ├─ Detect size preferences
   └─ Identify eco-comparison intent

2. Search products
   ├─ Fuzzy match product names (threshold: 60%)
   ├─ Semantic match descriptions
   └─ Filter by category

3. Rank by eco-score
   ├─ Sort by carbon_emission (ascending)
   ├─ Apply durability_score multiplier
   └─ Return top recommendations

4. Format response
   └─ Include carbon metrics, price, and why it's eco-friendly
```

---

## 📊 Database Schema

### Products Table
```sql
CREATE TABLE products (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(200) NOT NULL,
  category_id INT,
  price DECIMAL(10,2),
  cradle_to_warehouse_footprint DECIMAL(10,2),
  eco_points INT,
  description TEXT,
  image_url VARCHAR(1000),
  stock_quantity INT,
  is_archived TINYINT(1)
);
```

### Categories Table
```sql
CREATE TABLE categories_tb (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL UNIQUE,
  description VARCHAR(255)
);
```

### Product Materials Table
```sql
CREATE TABLE product_materials (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_id BIGINT,
  material_id INT,
  weight_kg DECIMAL(10,3),
  FOREIGN KEY (product_id) REFERENCES products(id)
);
```

### Materials Table
```sql
CREATE TABLE materials (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  eco_rating INT
);
```

---

## 🐛 Troubleshooting

### 1. **Module Not Found Errors**

**Error:** `ModuleNotFoundError: No module named 'flask_cors'`

**Solution:**
```bash
pip install -r requirements.txt
# or
pip install flask-cors
```

### 2. **Backend API Connection Failing**

**Error:** `⚠️ Backend API failed, using fallback CSV`

**Solution:**
- Verify backend is running on port 8080
- Check backend API endpoints are accessible:
  ```bash
  curl http://localhost:8080/api/v1/products
  ```
- Update `BACKEND_BASE_URL` if needed:
  ```bash
  export BACKEND_BASE_URL=http://your-backend-url:8080
  ```

### 3. **CORS Issues**

**Error:** `Access to XMLHttpRequest blocked by CORS policy`

**Solution:**
- Backend already has CORS enabled via `@CrossOrigin`
- Ensure Flask CORS is initialized in `app.py`
- Check browser console for exact error

### 4. **Port Already in Use**

**Error:** `Address already in use - port 5000`

**Solution:**
```bash
# Find and kill process on port 5000
# Windows (PowerShell)
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process

# macOS/Linux
lsof -ti:5000 | xargs kill -9

# Or use different port
python app.py --port 5001
```

### 5. **Chatbot Not Responding**

**Cause:** Backend API is unavailable

**Debug:**
```python
# In app.py, add logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test backend connectivity
import requests
response = requests.get("http://localhost:8080/api/v1/products")
print(response.status_code)
```

### 6. **Virtual Environment Issues**

**Error:** `The term 'python' is not recognized` (Windows)

**Solution:**
```bash
# Use full path
E:\EcoBazzarX\Github_files\ecobazaax-ai-recommendations-system-chatbot-v2\venv\Scripts\python.exe app.py

# Or activate venv first
.\venv\Scripts\Activate.ps1
python app.py
```

---

## 📁 Project Structure

```
ecobazaax-ai-recommendations-system-chatbot-v2/
│
├── app.py                          # Flask application entry point
├── chatbot_logic.py               # Core chatbot logic (549 lines)
├── requirements.txt               # Python dependencies
├── intents.json                   # Intent definitions
├── README_COMPREHENSIVE.md        # This file
│
├── recommender/                   # AI Recommendation Engine
│   ├── __init__.py
│   ├── recommender.py            # Recommender class (305 lines)
│   └── product_data.csv          # Fallback product data
│
├── backend_client/               # Backend API Client
│   ├── __init__.py
│   └── api_client.py            # API communication
│
├── data/                          # Data storage
│   └── session.json              # Session memory (fallback)
│
├── test_client.py                # Test client for chatbot
├── test_recommender.py           # Test recommender functionality
│
└── __pycache__/                  # Python cache (auto-generated)
```

---

## 🔄 Data Flow Examples

### Example 1: Product Recommendation

```
User Input: "Recommend an eco-friendly water bottle"
                    ↓
        Intent Detection: eco_recommendation
                    ↓
        Recommender.recommend("water bottle")
                    ↓
        Fuzzy Match: "bamboo water bottle" (score: 85%)
                    ↓
        Query Backend API: /api/v1/products/search?q=bottle
                    ↓
        Response: [
                    {id: 1, name: "Bamboo Water Bottle", carbon: 2.5kg},
                    {id: 2, name: "Plastic Bottle", carbon: 5.8kg}
                ]
                    ↓
        Rank by Carbon Footprint (ascending)
                    ↓
        Return: "🌿 I recommend Bamboo Water Bottle with 2.5kg CO₂e"
```

### Example 2: Add to Cart

```
User Input: "Add 2 bottles to cart"
                    ↓
        Intent Detection: cart_added
                    ↓
        Parse: product="bottles", quantity=2
                    ↓
        Find Product: via API search
                    ↓
        POST /api/v1/cart/add {productId: 1, quantity: 2}
                    ↓
        Response: ✅ Added to cart
                    ↓
        Return: "Bamboo Water Bottle added to your cart for ₹500 x 2! 🛒"
```

### Example 3: Checkout

```
User Input: "Checkout"
                    ↓
        Intent Detection: checkout
                    ↓
        GET /api/v1/cart
                    ↓
        Calculate Total: ₹2500
                    ↓
        Return: "Your total is ₹2500. Apply coupon? (SAVE15, ECO10, GREEN5)"
                    ↓
        Wait for next user input (coupon or confirm)
```

---

## 📞 Support & Contact

**Repository:** https://github.com/EcoBazaarX-Batch-4/ecobazaax-ai-recommendations-system-chatbot-v2

**Issues:** Report issues on GitHub Issues tab

**Developers:**
- EcoBazaarX Development Team
- Batch 4 Contributors

---

## 📄 License

This project is part of the EcoBazaarX initiative. See LICENSE file for details.

---

## 🎯 Future Enhancements

- [ ] Advanced NLP with BERT model
- [ ] Real-time product inventory sync
- [ ] User preference learning
- [ ] Carbon offset recommendations
- [ ] Gamification with eco-points
- [ ] Multi-language support
- [ ] Voice chat integration
- [ ] Analytics dashboard

---

**Last Updated:** December 2, 2025  
**Version:** 2.0  
**Status:** ✅ Production Ready
