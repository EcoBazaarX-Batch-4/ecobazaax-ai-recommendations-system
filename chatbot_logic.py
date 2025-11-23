"""
chatbot_logic.py — Full API mode (no local persistence)

Responsibilities:
- Intent detection (simple rule-based)
- Use backend REST API for:
    - product search (/api/v1/products/search)
    - cart operations (/api/v1/cart, /api/v1/cart/add, /api/v1/cart/remove/{id})
    - checkout (/api/v1/checkout)
    - orders / cancel (best-effort using common endpoints)
- Exposes:
    - chatbot_response(user_input, user_id="guest_user", jwt_token=None)
    - get_cart_items(user_id="guest_user", jwt_token=None)
    - get_cart_total(user_id="guest_user", jwt_token=None)
    - session_memory (ephemeral in-memory only)
Notes:
- Set BACKEND_BASE_URL environment variable (default: http://localhost:9091)
- This file intentionally does NOT write session JSON to disk.
"""

import os
import re
import json
import logging
import random
from datetime import datetime, timedelta

import requests
from requests import RequestException
from rapidfuzz import fuzz, process

from recommender.recommender import Recommender

# Basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chatbot_logic")

# -----------------------------
# Configuration
# -----------------------------
BACKEND_BASE_URL = os.environ.get("BACKEND_BASE_URL", "http://localhost:9091")
REQUEST_TIMEOUT = float(os.environ.get("REQUEST_TIMEOUT", 6.0))

# -----------------------------
# Ephemeral session memory (in-memory only)
# -----------------------------
session_memory = {
    "user_name": "Anoksha",
    "last_order": None,      # minimal tracking (non-persistent)
    "last_intent": None
}

# -----------------------------
# Local small fallbacks (not persisted)
# -----------------------------
related_products = {
    "eco bottle": "bamboo straw",
    "bamboo brush": "reusable bag",
    "reusable bag": "eco cup",
}

# -----------------------------
# HTTP helpers
# -----------------------------
def _make_headers(jwt_token=None):
    headers = {"Content-Type": "application/json"}
    if jwt_token:
        headers["Authorization"] = f"Bearer {jwt_token}"
    return headers

def backend_get(path, jwt_token=None, params=None):
    url = BACKEND_BASE_URL.rstrip("/") + path
    try:
        r = requests.get(url, headers=_make_headers(jwt_token), params=params, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        try:
            return r.json()
        except ValueError:
            return r.text
    except RequestException as e:
        logger.warning("backend_get error for %s : %s", url, e)
        return None

def backend_post(path, jwt_token=None, json_data=None):
    url = BACKEND_BASE_URL.rstrip("/") + path
    try:
        r = requests.post(url, headers=_make_headers(jwt_token), json=json_data, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        try:
            return r.json()
        except ValueError:
            return r.text
    except RequestException as e:
        logger.warning("backend_post error for %s : %s", url, e)
        return None

def backend_delete(path, jwt_token=None):
    url = BACKEND_BASE_URL.rstrip("/") + path
    try:
        r = requests.delete(url, headers=_make_headers(jwt_token), timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        try:
            return r.json() if r.text else {}
        except ValueError:
            return r.text
    except RequestException as e:
        logger.warning("backend_delete error for %s : %s", url, e)
        return None

# -----------------------------
# Product search via backend
# -----------------------------
def find_product_via_api(query, jwt_token=None):
    """
    Return a product dict with keys: id, name, price (or None)
    Uses: GET /api/v1/products/search?q=...
    """
    if not query:
        return None
    q = query.strip()
    res = backend_get("/api/v1/products/search", jwt_token=jwt_token, params={"q": q})
    if res is None:
        return None

    candidates = []
    # Common response shapes: list, or dict with items/content/newArrivals, etc.
    if isinstance(res, list):
        candidates = res
    elif isinstance(res, dict):
        for k in ("items", "content", "data", "results", "newArrivals"):
            if isinstance(res.get(k), list):
                candidates = res.get(k)
                break
        if not candidates:
            # try to pick any top-level list
            for v in res.values():
                if isinstance(v, list):
                    candidates = v
                    break

    if not candidates:
        return None

    # fuzzy-match names in candidates
    names = [c.get("name", "") for c in candidates]
    match = process.extractOne(q, names, scorer=fuzz.partial_ratio)
    if match and match[1] >= 60:
        matched_name = match[0]
        for c in candidates:
            if c.get("name") == matched_name:
                return {
                    "id": c.get("id"),
                    "name": c.get("name"),
                    "price": float(c.get("price") or 0)
                }

    # fallback -> return first candidate normalized
    first = candidates[0]
    return {"id": first.get("id"), "name": first.get("name"), "price": float(first.get("price") or 0)}

# -----------------------------
# Cart API wrappers (backend)
# -----------------------------
def api_add_to_cart(product_id, quantity=1, jwt_token=None):
    payload = {"productId": int(product_id), "quantity": int(quantity)}
    return backend_post("/api/v1/cart/add", jwt_token=jwt_token, json_data=payload)

def api_get_cart(jwt_token=None):
    return backend_get("/api/v1/cart", jwt_token=jwt_token)

def api_remove_cart_item(cart_item_id, jwt_token=None):
    return backend_delete(f"/api/v1/cart/remove/{cart_item_id}", jwt_token=jwt_token)

def api_clear_cart(jwt_token=None):
    """
    Clears cart by iterating through current cart items and deleting each.
    Returns True if best-effort succeeded, False otherwise.
    """
    cart = api_get_cart(jwt_token=jwt_token)
    if not cart or not isinstance(cart, dict):
        return False
    items = cart.get("items", [])
    success = True
    for it in items:
        item_id = it.get("cartItemId") or it.get("id") or it.get("cart_item_id")
        if item_id:
            r = api_remove_cart_item(item_id, jwt_token=jwt_token)
            if r is None:
                success = False
    return success

# -----------------------------
# Cart helper exports (used by app.py)
# -----------------------------
def get_cart_items(user_id="guest_user", jwt_token=None):
    """
    Returns list of cart items (normalised) or [].
    Keep signature compatible with app.py which may call get_cart_items(user_id).
    If jwt_token not provided, try anonymous cart.
    """
    cart = api_get_cart(jwt_token=jwt_token)
    if not cart or not isinstance(cart, dict):
        return []
    return cart.get("items", [])

def get_cart_total(user_id="guest_user", jwt_token=None):
    cart = api_get_cart(jwt_token=jwt_token)
    if not cart or not isinstance(cart, dict):
        return 0.0
    return float(cart.get("grandTotal") or cart.get("productsTotalAmount") or 0.0)

# -----------------------------
# High-level chat/cart functions
# -----------------------------
def handle_add_to_cart_api(user_input, user_id="guest_user", jwt_token=None):
    """
    Parses 'add X to cart' phrases, finds product via API, calls add-to-cart.
    Returns user-facing reply string.
    """
    qty = 1
    phrase = None
    m = re.search(r"add\s+(\d+)\s+(.+?)\s+(?:to\s+(?:my\s+)?cart|$)", user_input, re.IGNORECASE)
    if m:
        qty = int(m.group(1))
        phrase = m.group(2)
    else:
        m2 = re.search(r"add\s+(.+?)\s+(?:to\s+(?:my\s+)?cart|$)", user_input, re.IGNORECASE)
        if m2:
            phrase = m2.group(1)
        else:
            # fallback: use entirety
            phrase = user_input

    phrase = phrase.strip()
    product = find_product_via_api(phrase, jwt_token=jwt_token)
    if not product:
        # small local fallback: try simple known keys
        for k in related_products.keys():
            if k in user_input.lower():
                product = find_product_via_api(k, jwt_token=jwt_token) or {"id": None, "name": k.title(), "price": 0}
                break

    if not product or not product.get("id"):
        return "Sorry, I couldn’t find that product in our catalog. Try a simpler name or use the website search."

    res = api_add_to_cart(product["id"], quantity=qty, jwt_token=jwt_token)
    if res is None:
        return "⚠️ Could not add item to cart due to server error. Please try again."

    price = product.get("price", 0)
    product_name = product.get("name", "Item")
    related = related_products.get(product_name.lower(), "Reusable Bag").title()
    return f"{product_name} added to your cart for ₹{price} x {qty}! 🛒\nYou might also like {related} 🌱"

def show_cart_api(jwt_token=None):
    cart = api_get_cart(jwt_token=jwt_token)
    if not cart:
        return "⚠️ Could not retrieve cart. Please try again."

    items = cart.get("items", [])
    if not items:
        return "Your cart is empty. Add some products to get started! 🌿"

    lines = []
    # get total from different possible fields
    total = cart.get("grandTotal") or cart.get("productsTotalAmount") or 0
    for it in items:
        name = it.get("productName") or it.get("product_name") or it.get("name") or "Item"
        qty = it.get("quantity", 1)
        # prefer unit price fields if present
        unit_price = it.get("price") or it.get("pricePerItem") or it.get("price_per_item") or 0
        try:
            unit_price = float(unit_price or 0)
        except Exception:
            unit_price = 0.0
        lines.append(f"{name} (x{qty}) - ₹{unit_price * qty}")
    return f"You have {len(items)} items in your cart:\n" + "\n".join(lines) + f"\nTotal = ₹{total}"

def clear_cart_api(jwt_token=None):
    ok = api_clear_cart(jwt_token=jwt_token)
    if ok:
        return "🗑️ Your cart has been cleared!"
    return "⚠️ Could not clear cart at the moment. Try again."

# -----------------------------
# Checkout & order operations via backend
# -----------------------------
def checkout_cart_api(jwt_token=None):
    cart = api_get_cart(jwt_token=jwt_token)
    if not cart:
        return "🛒 Your cart is empty or cannot be fetched."

    total = cart.get("grandTotal") or cart.get("productsTotalAmount") or 0
    if not total or float(total) == 0:
        return "🛒 Your cart is empty!"

    # store ephemeral pending total for session only
    session_memory["pending_total"] = float(total)
    return f"Your total is ₹{int(float(total))}. 💸\nWould you like to apply a coupon code? (SAVE15, ECO10, GREEN5)"

def confirm_order_api(jwt_token=None):
    """
    Call backend checkout endpoint. Backend may expect cart in session or body.
    This function does a best-effort POST /api/v1/checkout with empty body (many backends use server-side cart).
    """
    if not jwt_token:
        return "Please login via frontend so I can place the order for you."

    res = backend_post("/api/v1/checkout", jwt_token=jwt_token, json_data={})
    if res is None:
        # fallback local ephemeral order
        order_id = f"ORD{random.randint(1000,9999)}"
        session_memory["last_order"] = {"order_id": order_id, "total": session_memory.get("pending_total", 0), "status": "Processing"}
        return f"✅ Order placed locally (backend failed). Order ID: {order_id}\nTotal: ₹{int(session_memory.get('pending_total',0))}"

    # expected backend response may include order id or order object
    order_id = res.get("orderId") or res.get("order_id") or res.get("id") or res.get("orderId", None)
    session_memory["last_order"] = {"order_id": order_id or "N/A", "total": session_memory.get("pending_total", 0), "status": "Processing"}
    return f"✅ Order placed successfully!\n🧾 Order ID: {order_id}\nTotal: ₹{int(session_memory.get('pending_total',0))}"

def track_order_api(jwt_token=None):
    """
    Try to fetch user orders from backend: GET /api/v1/profile/orders
    If not available, return ephemeral last_order.
    """
    if jwt_token:
        res = backend_get("/api/v1/profile/orders", jwt_token=jwt_token)
        if isinstance(res, list) and res:
            # pick most recent
            recent = res[0]
            status = recent.get("status") or recent.get("orderStatus") or "Unknown"
            order_id = recent.get("id") or recent.get("orderId") or recent.get("order_id")
            eta = datetime.now() + timedelta(hours=24)
            return f"📦 Order {order_id} status: {status}. Estimated delivery by {eta.strftime('%d %b %Y')}."
    # fallback ephemeral
    last = session_memory.get("last_order")
    if not last:
        return "You haven’t placed any orders yet."
    return f"📦 Order {last.get('order_id')} status: {last.get('status')}."

def cancel_order_api(jwt_token=None):
    """
    Attempt to cancel last order via backend; common pattern:
    POST /api/v1/profile/orders/{id}/cancel or POST /api/v1/admin/orders/{id}/cancel
    If backend doesn't support, fallback to ephemeral cancel.
    """
    last = session_memory.get("last_order")
    if not last or not last.get("order_id"):
        return "You haven’t placed any orders yet."

    od = last.get("order_id")
    if jwt_token:
        # try common endpoint pattern
        res = backend_post(f"/api/v1/profile/orders/{od}/cancel", jwt_token=jwt_token, json_data={})
        if res:
            last["status"] = "Cancelled"
            return f"🛑 Order {od} cancelled successfully on backend."
        # try alternate endpoint
        res2 = backend_post(f"/api/v1/orders/{od}/cancel", jwt_token=jwt_token, json_data={})
        if res2:
            last["status"] = "Cancelled"
            return f"🛑 Order {od} cancelled successfully on backend."
    # fallback ephemeral
    last["status"] = "Cancelled"
    return f"🛑 Order {od} has been cancelled (local)."

# -----------------------------
# Intent detection
# -----------------------------
def detect_intent(user_input):
    u = user_input.lower().strip()
    if re.search(r"\b(hi|hello|hey)\b", u): return "greeting"
    if "tip" in u: return "eco_tip"
    if re.search(r"\b(show|what|see|how many)\b.*\b(cart|basket)\b", u): return "cart_query"
    if re.search(r"\b(add|put)\b.*\b(cart|basket)\b", u): return "cart_added"
    if re.search(r"\b(remove|delete|take out)\b.*\b(from )?(my )?(cart|basket)\b", u):
        return "cart_remove_single"
    if re.search(r"\b(clear|empty|remove all)\b.*\b(cart|basket)\b", u): return "cart_clear"
    if re.search(r"\b(checkout|place order|buy now|purchase)\b", u): return "checkout"
    if re.search(r"\b(coupon|apply)\b", u): return "apply_coupon"
    if re.search(r"\b(upi|cod|net banking|wallet)\b", u): return "payment_method"
    if re.search(r"\b(confirm|finalize|complete)\b.*\b(order)?\b", u): return "confirm_order"
    if re.search(r"\b(track|status|where|delivery)\b.*\b(order|package|parcel)\b", u): return "track_order"
    if re.search(r"\b(cancel|abort|stop)\b.*\b(order|purchase|request)?\b", u): return "cancel_order"
    if re.search(r"\b(thank|bye|goodbye)\b", u): return "small_talk"
    if re.search(r"\b(recommend|suggest|eco friendly|eco-friendly|compare|alternative)\b", u): return "eco_recommendation"
    if re.search(r"(carbon|emission|eco[- ]?score|footprint)", u): return "eco_info"
    if re.search(r"\b(vs|versus|compare|difference between)\b", u): return "eco_comparison"
    return "unknown"

def remove_single_item_api(user_input, jwt_token=None):
    """
    Remove ONE specific product by fuzzy-matching item name.
    Example:
      - remove atomic habits from my cart
      - delete bomber jacket
      - take out bottle
    """
    # Extract product name
    m = re.search(r"(remove|delete|take out)\s+(.+?)\s+(from\s+)?(my\s+)?(cart|basket)", user_input, re.IGNORECASE)
    if m:
        phrase = m.group(2).strip()
    else:
        m2 = re.search(r"(remove|delete|take out)\s+(.+)", user_input, re.IGNORECASE)
        phrase = m2.group(2).strip() if m2 else user_input.strip()

    # Step 1: Fetch cart
    cart = api_get_cart(jwt_token)
    if not cart:
        return "⚠️ Could not access your cart."

    items = cart.get("items", [])
    if not items:
        return "Your cart is empty."

    # Step 2: Fuzzy match item name
    names = [item.get("productName", "") for item in items]
    match = process.extractOne(phrase.lower(), [n.lower() for n in names], scorer=fuzz.partial_ratio)

    if not match or match[1] < 60:
        return f"⚠️ I couldn’t find '{phrase}' in your cart."

    matched_name = match[0]

    # Find item object
    target_item = None
    for it in items:
        if it.get("productName", "").lower() == matched_name:
            target_item = it
            break

    if not target_item:
        return f"⚠️ Could not remove '{phrase}'."

    cart_item_id = target_item.get("cartItemId")
    if not cart_item_id:
        return "⚠️ Could not find cart item ID."

    # Step 3: Call backend DELETE
    res = api_remove_cart_item(cart_item_id, jwt_token)
    if res is None:
        return "⚠️ Failed to remove item due to server error."

    return f"🗑️ Removed **{target_item.get('productName')}** from your cart."


# =======================================================================
#                          MAIN CHATBOT RESPONSE
# =======================================================================

def chatbot_response(user_input, user_id="guest_user", jwt_token=None):
    """
    Main function called by app.py.
    """
    intent = detect_intent(user_input)
    session_memory["last_intent"] = intent

    # -----------------------------------
    # GREETINGS
    # -----------------------------------
    if intent == "greeting":
        return f"Hey {session_memory.get('user_name', 'User')} 👋! Welcome back to EcoBazaarX. How can I help you today?"

    if intent == "eco_tip":
        tips = [
            "Switch to reusable bottles to reduce single-use plastic.",
            "Carry your own shopping bag instead of plastic ones.",
            "Opt for bamboo toothbrushes — they decompose naturally.",
            "Save water by turning off the tap while brushing."
        ]
        return random.choice(tips)

    # -----------------------------------
    # CART OPERATIONS
    # -----------------------------------
    if intent == "cart_added":
        return handle_add_to_cart_api(user_input, user_id=user_id, jwt_token=jwt_token)

    if intent == "cart_query":
        return show_cart_api(jwt_token=jwt_token)

    if intent == "cart_clear":
        return clear_cart_api(jwt_token=jwt_token)

    if intent == "cart_remove_single":
        return remove_single_item_api(user_input, jwt_token=jwt_token)


    # -----------------------------------
    # CHECKOUT FLOW
    # -----------------------------------
    if intent == "checkout":
        return checkout_cart_api(jwt_token=jwt_token)

    if intent == "apply_coupon":
        m = re.search(r"(save15|eco10|green5)", user_input, re.IGNORECASE)
        if not m:
            return "Please mention a valid coupon code (SAVE15, ECO10, GREEN5)."
        code = m.group(1).upper()
        return f"✅ Coupon {code} noted. Please confirm payment to apply it during checkout."

    if intent == "payment_method":
        m = re.search(r"(upi|cod|net banking|wallet)", user_input, re.IGNORECASE)
        if m:
            return f"Payment method set to {m.group(1).upper()}. Please confirm your order."
        return "Please choose UPI, COD, Net Banking or Wallet."

    if intent == "confirm_order":
        return confirm_order_api(jwt_token=jwt_token)

    if intent == "track_order":
        return track_order_api(jwt_token=jwt_token)

    if intent == "cancel_order":
        return cancel_order_api(jwt_token=jwt_token)

    # -----------------------------------
    # SMALL TALK
    # -----------------------------------
    if intent == "small_talk":
        if "thank" in user_input.lower():
            return "You're welcome — glad to help! 💚"
        return "Goodbye! Stay eco-friendly 🌿"

    # -----------------------------------
    # ECO RECOMMENDER
    # -----------------------------------
    if intent in ("eco_recommendation", "eco_info", "eco_comparison"):
        rec = Recommender()
        result = rec.recommend(user_input)

        if result.get("success"):
            p = result["recommended"]
            name = p.get("name") if isinstance(p, dict) else p["name"]
            reason = result.get("reason", "")

            if intent == "eco_info":
                ce = p.get("carbon_emission") if isinstance(p, dict) else p["carbon_emission"]
                return f"🌍 {name} has a carbon emission of {ce} kg CO₂e."

            return f"🌿 I recommend **{name}** — {reason}"

        return result.get("message", "Sorry, I couldn't find a match.")

    # -----------------------------------
    # DEFAULT
    # -----------------------------------
    return "Sorry, I didn’t quite get that. Could you rephrase?"
