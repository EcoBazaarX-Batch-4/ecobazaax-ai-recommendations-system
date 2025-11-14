import json
import os
import random
import re
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from recommender.recommender import Recommender

# -----------------------------
# 🗺️ City–State Mapping (India)
# -----------------------------
CITY_STATE_MAP = {
    "bhubaneswar": "odisha",
    "cuttack": "odisha",
    "rourkela": "odisha",
    "sambalpur": "odisha",
    "puri": "odisha",
    "kolkata": "west bengal",
    "ranchi": "jharkhand",
    "patna": "bihar",
    "delhi": "delhi",
    "mumbai": "maharashtra",
    "pune": "maharashtra",
    "bangalore": "karnataka",
    "chennai": "tamil nadu",
    "hyderabad": "telangana",
    "lucknow": "uttar pradesh",
    "noida": "uttar pradesh",
    "ahmedabad": "gujarat",
    "jaipur": "rajasthan",
    "kochi": "kerala",
    "guwahati": "assam",
    "bhopal": "madhya pradesh"
}

# -----------------------------
# 📍 Delivery Zone Helper Function
# -----------------------------
def get_delivery_zone(source_city, destination_city):
    """Classify delivery as intra-city, intra-state, or inter-state."""
    source_city = source_city.lower().strip()
    destination_city = destination_city.lower().strip()

    source_state = CITY_STATE_MAP.get(source_city)
    dest_state = CITY_STATE_MAP.get(destination_city)

    if not source_state or not dest_state:
        return "Unknown Zone"

    if source_city == destination_city:
        return "Intra-City"
    elif source_state == dest_state:
        return "Intra-State"
    else:
        return "Inter-State"

# -----------------------------
# 🧠 Session memory
# -----------------------------
session_memory = {
    "cart_items": 0,
    "last_intent": None,
    "last_order": None,
    "user_name": "Anoksha",
    "selected_payment": None,
    "delivery_city": None  
}

# -----------------------------
# 💾 Session Persistence (Save / Load JSON)
# -----------------------------
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "session.json")

def save_session_data():
    """Save carts and session memory to JSON file."""
    try:
        data = {
            "user_carts": user_carts,
            "session_memory": session_memory
        }
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        with open(DATA_PATH, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print("⚠️ Error saving session data:", e)

def load_session_data():
    """Load carts and session memory from JSON file."""
    global user_carts, session_memory
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r") as f:
                data = json.load(f)
            user_carts = data.get("user_carts", {})
            session_memory.update(data.get("session_memory", {}))
            print("✅ Session data loaded successfully.")
        except Exception as e:
            print("⚠️ Error loading session data:", e)

# -----------------------------
# 🔄 Load session data at startup
# -----------------------------
load_session_data()

# -----------------------------
# ♻️ Recommendation System
# -----------------------------
recommender = Recommender()

# -----------------------------
# 🛍️ Product Catalog
# -----------------------------
products = {
    "eco bottle": {"price": 150, "category": "kitchen", "desc": "Reusable steel eco-bottle with BPA-free design."},
    "bamboo brush": {"price": 80, "category": "personal care", "desc": "Eco toothbrush made of bamboo handle."},
    "reusable bag": {"price": 120, "category": "lifestyle", "desc": "Foldable reusable bag for everyday shopping."},
    "bamboo straw": {"price": 60, "category": "kitchen", "desc": "Pack of eco-friendly reusable bamboo straws."},
    "metal straw": {"price": 100, "category": "kitchen", "desc": "Durable stainless steel straw set."},
    "eco cup": {"price": 90, "category": "kitchen", "desc": "Reusable eco cup for coffee or tea."}
}

related_products = {
    "eco bottle": "bamboo straw",
    "bamboo brush": "reusable bag",
    "reusable bag": "eco cup",
    "bamboo straw": "eco bottle",
    "metal straw": "eco cup",
    "eco cup": "metal straw"
}

eco_tips = [
    "🌱 Tip: Switch to reusable bottles to reduce single-use plastic.",
    "♻️ Tip: Carry your own shopping bag instead of plastic ones.",
    "🌍 Tip: Opt for bamboo toothbrushes—they decompose naturally.",
    "💧 Tip: Save water by turning off the tap while brushing."
]

valid_coupons = {
    "SAVE15": 15,
    "ECO10": 10,
    "GREEN5": 5
}

# -----------------------------
# 🛒 Cart System
# -----------------------------
user_carts = {}  # key = user_id, value = list of items (dicts with name + price)

def get_cart_items(user_id="user123"):
    return user_carts.get(user_id, [])

def add_to_cart(user_id, item_name, price):
    user_carts.setdefault(user_id, []).append({"item": item_name.title(), "price": price})
    save_session_data()

def get_cart_total(user_id="user123"):
    return sum(item["price"] for item in user_carts.get(user_id, []))

def clear_cart(user_id="user123"):
    user_carts[user_id] = []
    save_session_data()

def handle_add_to_cart(user_input, user_id="user123"):
    for product, details in products.items():
        if product in user_input.lower():
            add_to_cart(user_id, product, details["price"])
            return f"{product.title()} added to your cart for ₹{details['price']}! 🛒\nYou might also like {related_products.get(product, 'Reusable Bag').title()} 🌱"
    return "Sorry, I couldn’t find that product. Try adding something else!"

# -----------------------------
# 💳 Checkout & Order System
# -----------------------------
def checkout_cart(user_id="user123"):
    items = get_cart_items(user_id)
    if not items:
        return "🛒 Your cart is empty! Add some eco items first."

    total = get_cart_total(user_id)
    session_memory["cart_items"] = 0
    session_memory["pending_total"] = total
    session_memory["coupon_applied"] = None
    session_memory["selected_payment"] = None

    return f"Your total is ₹{total}. 💸\nWould you like to apply a coupon code? (Available: SAVE15, ECO10, GREEN5)"

def apply_coupon(code, user_id="user123"):
    code = code.upper()
    if code not in valid_coupons:
        return f"❌ Invalid coupon code '{code}'. Please try again."

    discount = valid_coupons[code]
    total = session_memory.get("pending_total", 0)
    discounted_total = total - (total * discount / 100)
    session_memory["pending_total"] = int(discounted_total)
    session_memory["coupon_applied"] = code

    return f"✅ Coupon '{code}' applied successfully! You saved {discount}%.\nNew total: ₹{int(discounted_total)}.\nNow choose your payment method (UPI / COD / Net Banking / Wallet)."

def select_payment_method(method, user_id="user123"):
    methods = ["upi", "cod", "net banking", "wallet"]
    method = method.lower()

    if method not in methods:
        return "❌ Invalid payment method. Please choose from UPI, COD, Net Banking, or Wallet."

    session_memory["selected_payment"] = method
    return (
        f"💳 Payment method '{method.upper()}' selected.\n"
        "📍 Please provide your delivery city (e.g., Bhubaneswar, Rourkela, Mumbai) before confirming your order."
    )

def confirm_order(user_id="user123"):
    items = get_cart_items(user_id)
    if not items:
        return "🛒 Your cart is empty!"

    total = session_memory.get("pending_total", 0)
    payment = session_memory.get("selected_payment")
    if not payment:
        return "Please select a payment method before confirming."

    delivery_city = session_memory.get("delivery_city")
    if not delivery_city:
        return "📍 Please provide your delivery city before confirming your order."

    source_city = "Bhubaneswar"  # warehouse
    destination_city = delivery_city
    delivery_zone = get_delivery_zone(source_city, destination_city)

    order_id = f"ORD{random.randint(1000, 9999)}"
    user_carts[user_id] = []

    session_memory["last_order"] = {
        "order_id": order_id,
        "items": [item["item"] for item in items],
        "total": total,
        "payment": payment.title(),
        "status": "Processing",
        "source_city": source_city,
        "destination_city": destination_city,
        "delivery_zone": delivery_zone
    }

    save_session_data()

    coupon_msg = ""
    if session_memory.get("coupon_applied"):
        coupon_msg = f"\n💚 Coupon {session_memory['coupon_applied']} applied."

    return (
        f"✅ Order placed successfully!\n"
        f"🧾 Order ID: {order_id}\n"
        f"Items: {', '.join([item['item'] for item in items])}\n"
        f"Total: ₹{total}\n"
        f"Payment Method: {payment.upper()}{coupon_msg}\n"
        f"🚚 Delivery Type: {delivery_zone}\n"
        f"Thanks for shopping sustainably! 🌿"
    )

def track_order(user_id="user123"):
    order = session_memory.get("last_order")
    if not order:
        return "You haven’t placed any orders yet."

    if order["status"].lower() == "cancelled":
        return f"❌ Order {order['order_id']} was cancelled. No delivery will be made."

    if order["status"].lower() == "delivered":
        return f"📦 Order {order['order_id']} has already been delivered. Hope you liked it! 💚"

    statuses = ["Processing", "Shipped", "Out for Delivery", "Delivered"]
    current_status = order["status"]

    if current_status not in statuses:
        return f"⚠️ Unknown order status for {order['order_id']}."

    next_status = statuses[min(statuses.index(current_status) + 1, len(statuses) - 1)]
    order["status"] = next_status
    save_session_data()

    order_id = order["order_id"]
    items = ", ".join(order["items"])
    delivery_zone = order.get("delivery_zone", "Unknown")

    future_eta = datetime.now() + timedelta(hours=2)
    eta = future_eta.strftime("%d %b %Y, %I:%M %p")

    return f"📦 Order {order_id} ({items}) is now *{order['status']}*.\n🚚 Delivery Type: {delivery_zone}\nExpected delivery by {eta}."

def cancel_order(user_id="user123"):
    order = session_memory.get("last_order")

    if not order:
        return "❌ You haven’t placed any orders yet."

    if order["status"].lower() in ["delivered", "cancelled"]:
        return f"⚠️ Order {order['order_id']} is already {order['status']}."

    order["status"] = "Cancelled"
    save_session_data()

    return f"🛑 Order {order['order_id']} has been cancelled successfully. Refunds (if any) will be processed soon. 💚"

# -----------------------------
# 🤖 Intent Detection
# -----------------------------
def detect_intent(user_input):
    user_input = user_input.lower().strip()

    if re.search(r"\b(hi|hello|hey)\b", user_input): return "greeting"
    if "tip" in user_input: return "eco_tip"
    if re.search(r"(kitchen|personal care|lifestyle)", user_input): return "category"
    if re.search(r"\b(show|find|search|see|suggest)\b.*(product|item|bottle|straw|bag|cup|brush)", user_input): return "product_search"
    if re.search(r"\b(details|info|about)\b.*", user_input): return "product_detail"
    if re.search(r"\b(add|put)\b.*\b(cart|basket)\b", user_input): return "cart_added"
    if re.search(r"\b(remove|delete|take out)\b.*\b(cart|basket)\b", user_input): return "cart_removed"
    if re.search(r"\b(show|what|see|how many)\b.*\b(cart|basket|product)\b", user_input): return "cart_query"
    if re.search(r"\b(checkout|place order|buy now|purchase)\b", user_input): return "checkout"
    if re.search(r"\b(coupon|apply)\b", user_input): return "apply_coupon"
    if re.search(r"\b(upi|cod|net banking|wallet)\b", user_input): return "payment_method"
    if re.search(r"\b(confirm|done|finalize|complete)\b.*\b(order)?\b", user_input): return "confirm_order"
    if re.search(r"\b(track|status|where|delivery|progress)\b.*\b(order|package|parcel|delivery)\b", user_input): return "track_order"
    if re.search(r"\b(cancel|abort|stop)\b.*\b(order|purchase|request)?\b", user_input): return "cancel_order"
    if re.search(r"\b(thank|bye|goodbye)\b", user_input): return "small_talk"
    if re.search(r"\b(recommend|suggest|eco friendly|compare|alternative|which is more eco[- ]?friendly)\b", user_input):
        return "eco_recommendation"
    if re.search(r"(carbon|emission|eco[- ]?score|environmental impact|eco rating|footprint)", user_input):
        return "eco_info"
    if re.search(r"\b(vs|versus|compare|difference between)\b", user_input):
        return "eco_comparison"

    return "unknown"

# -----------------------------
# 💬 Chatbot Response
# -----------------------------
def chatbot_response(user_input, user_id="user123"):
    intent = detect_intent(user_input)

    if intent == "greeting":
        return f"Hey {session_memory['user_name']} 👋! Welcome back to EcoBazaarX. How can I help you today?"
    if intent == "eco_tip":
        return random.choice(eco_tips)
    if intent == "cart_added":
        return handle_add_to_cart(user_input, user_id)
    if intent == "cart_removed":
        clear_cart(user_id)
        return "🗑️ Your cart has been cleared!"
    if intent == "cart_query":
        items = get_cart_items(user_id)
        if not items:
            return "Your cart is empty. Add some eco products to get started! 🌿"
        total = get_cart_total(user_id)
        item_list = ", ".join([i["item"] for i in items])
        return f"You have {len(items)} items in your cart: {item_list}. Total = ₹{total}."
    if intent == "checkout":
        return checkout_cart(user_id)
    if intent == "apply_coupon":
        match = re.search(r"(save15|eco10|green5)", user_input, re.IGNORECASE)
        if not match:
            return "Please mention a valid coupon code."
        return apply_coupon(match.group(1), user_id)
    if intent == "payment_method":
        match = re.search(r"(upi|cod|net banking|wallet)", user_input, re.IGNORECASE)
        return select_payment_method(match.group(1), user_id)
    # 🆕 Detect if user just entered a city name
    if user_input.lower() in CITY_STATE_MAP:
        session_memory["delivery_city"] = user_input.title()
        save_session_data()
        return f"📦 Got it! Delivery city set to {session_memory['delivery_city']}.\nYou can now confirm your order."
    if intent == "confirm_order":
        return confirm_order(user_id)
    if intent == "confirm_order":
        return confirm_order(user_id)
    if intent == "track_order":
        return track_order(user_id)
    if intent == "cancel_order":
        return cancel_order(user_id)
    if intent == "small_talk":
        if "thank" in user_input:
            return "You're very welcome! 💚 Keep shopping sustainably."
        return "Goodbye 👋 Stay eco-friendly!"
    if intent == "eco_recommendation":
        result = recommender.recommend(user_input)
        if result["success"]:
            product = result["recommended"]
            return f"🌿 I recommend **{product['name']}** — {result['reason']}"
        else:
            return "Sorry, I couldn’t find a matching product to recommend."
    if intent == "eco_info":
        result = recommender.recommend(user_input)
        if result.get("success"):
            product = result["recommended"]
            return (
                f"🌍 The product **{product['name']}** has a carbon emission of "
                f"{product['carbon_emission']} kg CO₂e.\n"
                f"That means it's more eco-friendly than its alternatives!"
            )
        else:
            return "Sorry, I couldn’t find emission details for that product."

    if intent == "eco_comparison":
        # Extract product names around 'vs', 'compare', or 'difference between'
        match = re.search(r"(\b[a-z ]+\b)\s*(?:vs|versus|compare|difference between)\s*(\b[a-z ]+\b)", user_input)
        if not match:
            return "Please specify two products to compare, e.g., 'bamboo brush vs plastic brush'."

        prod1, prod2 = match.groups()
        prod1, prod2 = prod1.strip(), prod2.strip()

        # 🧠 Use the recommender's built-in comparison method
        result = recommender.compare_products(prod1, prod2)

        if not result.get("success"):
            return f"Sorry, I couldn’t find enough data to compare **{prod1.title()}** and **{prod2.title()}**."

        better = result["recommended"]
        reason = result["reason"]

        return f"🌿 {better['name']} is more eco-friendly! 🌍\n{reason}"

    return "Sorry, I didn’t quite get that. Could you rephrase?"
