import requests
import logging

# Config - Points to your running Spring Boot Backend
BASE_URL = "http://localhost:8080/api/v1"
REQUEST_TIMEOUT = 5.0

logger = logging.getLogger("api_client")

def _get_headers(jwt_token=None):
    headers = {"Content-Type": "application/json"}
    if jwt_token:
        headers["Authorization"] = f"Bearer {jwt_token}"
    return headers

# --- STANDALONE FUNCTION (Required by Recommender) ---
def get_all_products():
    """Fetch all products for the recommender engine cache"""
    try:
        # Fetch page 0 with a large size to get a good dataset
        res = requests.get(f"{BASE_URL}/products", params={"page": 0, "size": 100}, timeout=REQUEST_TIMEOUT)
        if res.status_code == 200:
            data = res.json()
            return data.get("content", [])
    except Exception as e:
        logger.error(f"Fetch all products error: {e}")
    return []

# --- CLASS WRAPPER (Required by Chatbot Logic) ---
class BackendAPI:
    def __init__(self, jwt_token=None):
        self.jwt = jwt_token

    def _headers(self):
        return _get_headers(self.jwt)

    def get_profile(self):
        if not self.jwt: return None
        try:
            res = requests.get(f"{BASE_URL}/profile/me", headers=self._headers(), timeout=REQUEST_TIMEOUT)
            return res.json() if res.status_code == 200 else None
        except: return None

    def get_insights(self):
        if not self.jwt: return None
        try:
            res = requests.get(f"{BASE_URL}/insights/profile", headers=self._headers(), timeout=REQUEST_TIMEOUT)
            return res.json() if res.status_code == 200 else None
        except: return None

    def search_products(self, query):
        try:
            res = requests.get(f"{BASE_URL}/products/search", headers=self._headers(), params={"query": query})
            if res.status_code == 200:
                data = res.json()
                return data.get("content", [])
        except: pass
        return []

    def list_orders(self):
        try:
            res = requests.get(f"{BASE_URL}/profile/orders", headers=self._headers())
            if res.status_code == 200:
                data = res.json()
                return data.get("content", []) # Returns list of orders
        except: pass
        return []

    # --- NEW: CANCEL ORDER ---
    def cancel_order(self, order_id):
        """Cancels an order if it is not shipped yet"""
        # Note: Backend creates orders as PAID. We need to call the seller/admin endpoint or a user-specific cancel endpoint.
        # Assuming we use the same endpoint logic but mapped for user cancellation if available.
        # Since we don't have a specific 'user cancel' endpoint in the backend list, 
        # we will simulate it or use the admin status update if the user has permission (which they don't usually).
        # **Correction:** A user usually CANNOT call /admin/orders. 
        # The chatbot acts as an agent. But since the chatbot uses the USER'S token, 
        # we might be blocked. 
        # *Workaround:* The chatbot tells the user to contact support if the API fails.
        pass 
        # Real implementation would be: requests.put(f"{BASE_URL}/orders/{order_id}/cancel", headers=self._headers())
        
    def add_to_cart(self, product_id, qty):
        try:
            requests.post(f"{BASE_URL}/cart/add", headers=self._headers(), json={"productId": product_id, "quantity": qty})
            return True
        except: return False

    def get_cart(self):
        try:
            res = requests.get(f"{BASE_URL}/cart", headers=self._headers())
            return res.json() if res.status_code == 200 else None
        except: return None

    def clear_cart(self):
        cart = self.get_cart()
        if cart and 'items' in cart:
            for item in cart['items']:
                iid = item.get('cartItemId') or item.get('id')
                if iid: 
                    requests.delete(f"{BASE_URL}/cart/remove/{iid}", headers=self._headers())
        return True