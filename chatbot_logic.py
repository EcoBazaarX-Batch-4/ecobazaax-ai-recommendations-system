import logging
import re
import random
from backend_client.api_client import BackendAPI
from recommender.recommender import EcoRecommender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chatbot_logic")

recommender = EcoRecommender()

# --- 1. EDUCATIONAL FEATURES (NEW) ---

def handle_about_app():
    return (f"🌱 **EcoBazaarX** is a smart sustainable marketplace.\n\n"
            f"Unlike regular stores, we use a **Carbon Engine** to calculate the environmental cost of every product. "
            f"Our goal is to help you make greener choices and track your positive impact on the planet! 🌍")

def handle_carbon_definition():
    return (f"👣 **Carbon Footprint**:\n"
            f"This is the total amount of greenhouse gases (like CO₂) emitted to create a product.\n\n"
            f"It includes emissions from farming materials, factory energy, and shipping the item to you. "
            f"Lower footprint = Better for Earth! 📉")

def handle_lca_info():
    return (f"♻️ **What is LCA?**\n"
            f"**LCA (Life Cycle Assessment)** is the scientific method we use to score products.\n"
            f"We analyze 4 stages:\n"
            f"1. **Materials:** (e.g. Cotton farming)\n"
            f"2. **Manufacturing:** (Factory energy)\n"
            f"3. **Packaging:** (Box vs Plastic)\n"
            f"4. **Transport:** (Shipping distance)\n\n"
            f"This gives us the true 'Cradle-to-Warehouse' carbon score.")

# --- 2. EXISTING FEATURES ---

def handle_rank_inquiry(api):
    user = api.get_profile()
    if not user:
        return "🔒 Please log in to see your Eco Rank!"
    
    points = user.get("ecoPoints", 0)
    rank_level = user.get("rankLevel", 0)
    ranks = ["Sprout 🌱", "Sapling 🌿", "Guardian 🛡️", "Eco-Hero 🦸", "Earth-Warden 🌍", "Planet-Savior 🌟"]
    current_rank = ranks[rank_level] if rank_level < len(ranks) else "Planet-Savior 🌟"
    
    return (f"🏆 **Status Report**:\n"
            f"You are currently a **{current_rank}** ({points} Eco Points).\n"
            f"Keep shopping sustainably to rank up!")

def handle_impact_inquiry(api):
    insights = api.get_insights()
    if not insights:
        return "🔒 Log in to track your environmental impact!"
    
    carbon_saved = insights.get("lifetimeTotalCarbon", 0.0) or 0.0
    trees = round(carbon_saved / 20, 1)
    
    return (f"🌍 **Your Impact**:\n"
            f"You have saved **{carbon_saved} kg** of CO₂.\n"
            f"That's equivalent to planting **{trees} trees**! 🌳")

def handle_order_tracking(api):
    orders = api.list_orders()
    if not orders:
        return "You haven't placed any orders yet."
    
    last_order = orders[0]
    status = last_order.get("status", "Processing")
    return f"📦 **Order #{last_order['id']}** is currently **{status}**."

def handle_cart(api, user_input):
    u = user_input.lower()
    if "show" in u or "view" in u:
        cart = api.get_cart()
        if not cart or not cart.get('items'): return "Your cart is empty."
        msg = "🛒 **Cart:**\n" + "\n".join([f"- {i['productName']} (x{i['quantity']})" for i in cart['items']])
        return msg + f"\n**Total:** ₹{cart.get('grandTotal', 0)}"
    
    if "clear" in u:
        return "🗑️ Cart cleared." if api.clear_cart() else "Failed to clear cart."
        
    return "I can help with your cart! Say 'Show cart' or 'Clear cart'."

# --- MAIN ROUTER ---
def chatbot_response(user_input, user_id="guest", jwt_token=None):
    api = BackendAPI(jwt_token)
    u = user_input.lower()
    
    # 1. Definitions & Education
    if "what is" in u or "define" in u or "tell me about" in u:
        if "eco" in u and "bazaar" in u: return handle_about_app()
        if "carbon" in u and "footprint" in u: return handle_carbon_definition()
        if "lca" in u or "life cycle" in u: return handle_lca_info()

    if any(x in u for x in ["how", "calculate", "formula"]):
        return handle_lca_info()

    # 2. Gamification
    if any(x in u for x in ["rank", "level", "points", "status"]):
        return handle_rank_inquiry(api)
    
    # 3. Impact
    if any(x in u for x in ["impact", "carbon", "saved"]):
        return handle_impact_inquiry(api)

    # 4. Orders
    if any(x in u for x in ["track", "order", "delivery"]):
        return handle_order_tracking(api)
    
    # 5. Cart
    if "cart" in u:
        return handle_cart(api, u)

    # 6. Recommendations (Fallback)
    clean_query = u.replace("find", "").replace("search", "").replace("looking for", "").strip()
    return recommender.recommend(clean_query)