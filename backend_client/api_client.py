import requests

BASE_URL = "http://localhost:9091/api/v1"

class BackendAPI:
    """
    Wrapper for all backend REST API calls.
    The chatbot never talks to MySQL directly; everything goes via this class.
    """

    def __init__(self, jwt_token=None):
        self.jwt = jwt_token

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.jwt:
            h["Authorization"] = f"Bearer {self.jwt}"
        return h

    # ---------------------------
    # AUTH
    # ---------------------------
    def login(self, email, password):
        url = f"{BASE_URL}/auth/login"
        res = requests.post(url, json={"email": email, "password": password})
        if res.status_code == 200:
            return res.json()
        return None

    # ---------------------------
    # PRODUCTS
    # ---------------------------
    def search_products(self, query):
        url = f"{BASE_URL}/products/search?q={query}"
        res = requests.get(url, headers=self._headers())
        return res.json()

    def get_product(self, product_id):
        url = f"{BASE_URL}/products/{product_id}"
        res = requests.get(url, headers=self._headers())
        return res.json()

    # ---------------------------
    # CART
    # ---------------------------
    def get_cart(self):
        url = f"{BASE_URL}/cart"
        res = requests.get(url, headers=self._headers())
        return res.json()

    def add_to_cart(self, product_id, qty):
        url = f"{BASE_URL}/cart/add"
        res = requests.post(url, headers=self._headers(),
                            json={"productId": product_id, "quantity": qty})
        return res.json()

    def remove_from_cart(self, cart_item_id):
        url = f"{BASE_URL}/cart/remove/{cart_item_id}"
        res = requests.delete(url, headers=self._headers())
        return res.json()

    def clear_cart(self):
        url = f"{BASE_URL}/cart/clear"
        res = requests.post(url, headers=self._headers())
        return res.json()

    # ---------------------------
    # CHECKOUT
    # ---------------------------
    def checkout(self):
        url = f"{BASE_URL}/checkout"
        res = requests.post(url, headers=self._headers())
        return res.json()

    # ---------------------------
    # ORDERS
    # ---------------------------
    def list_orders(self):
        url = f"{BASE_URL}/profile/orders"
        res = requests.get(url, headers=self._headers())
        return res.json()

    def get_order(self, order_id):
        url = f"{BASE_URL}/profile/orders/{order_id}"
        res = requests.get(url, headers=self._headers())
        return res.json()

