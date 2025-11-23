# recommender/recommender.py
import pandas as pd
import re
import os
from rapidfuzz import fuzz, process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import mysql.connector

# ==============================================
# 🌍 PHASE 1: Category normalization & synonyms
# ==============================================
CATEGORY_SYNONYMS = {
    "bottle": "drinkware",
    "cup": "drinkware",
    "bag": "shopping bag",
    "brush": "hygiene",
    "comb": "hygiene",
    "plate": "kitchen",
    "straw": "kitchen"
}

# ==============================================
# 🧼 PHASE 2: Text preprocessing helper
# ==============================================
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'(.)\1{2,}', r'\1', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ==============================================
# 🔍 PHASE 3: Fuzzy & semantic matching
# ==============================================
def fuzzy_find(term, choices, threshold=70):
    if not term or not choices:
        return None
    match = process.extractOne(term, choices, scorer=fuzz.partial_ratio)
    if match and match[1] >= threshold:
        return match[0]
    return None

def semantic_match(query, choices, top_n=1):
    if not choices:
        return None
    try:
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([query] + choices)
        cosine_sim = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
        best_idx = cosine_sim.argsort()[-top_n:][::-1]
        best_matches = [(choices[i], cosine_sim[i]) for i in best_idx]
        if best_matches and best_matches[0][1] > 0.25:
            return best_matches[0][0]
    except Exception:
        return None
    return None

# ==============================================
# 🌿 PHASE 4: Main Recommender class (MySQL-backed)
# ==============================================
class Recommender:
    def __init__(self):
        # --------------------------
        # 🔗 Connect to MySQL (edit credentials)
        # --------------------------
        # Replace with the actual credentials that work on your machine
        self.conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",         # <-- change if needed
            password="password",     # <-- change to your password
            database="ecobazaarx"
        )

        # --------------------------
        # 🔎 Load products + category name
        # --------------------------
        query = """
        SELECT 
        id,
        name,
        category,
        material,
        size,
        type,
        carbon_emission,
        durability_score,
        price,
        description,
        brand
        FROM eco_products
        """

        
        df = pd.read_sql(query, self.conn)
        df["category_norm"] = df["category"].astype(str).str.lower().str.strip()
        df["size_norm"] = df["size"].astype(str).str.lower().str.strip()
        df["type_norm"] = df["type"].astype(str).str.lower().str.strip()
        df["name_norm"] = df["name"].astype(str).apply(clean_text)



        # --------------------------
        # Map DB columns to the fields your recommender expects
        # --------------------------
        # carbon_emission <- cradle_to_warehouse_footprint
        df.rename(columns={
            "cradle_to_warehouse_footprint": "carbon_emission",
            "category_name": "category",
            "eco_points": "durability_score"   # reuse eco_points as a durability proxy
        }, inplace=True)

        # Fill missing columns your logic expects
        if "material" not in df.columns:
            df["material"] = None
        if "size" not in df.columns:
            df["size"] = None
        if "type" not in df.columns:
            df["type"] = None
        if "brand" not in df.columns:
            df["brand"] = None
        if "description" not in df.columns:
            df["description"] = ""

        # --------------------------
        # Infer product 'type' (eco / non-eco) using a data-driven threshold
        # (helps avoid a fixed arbitrary cutoff)
        # --------------------------
        # If carbon_emission is missing or zero, fill with small positive to avoid issues
        df["carbon_emission"] = pd.to_numeric(df["carbon_emission"], errors="coerce").fillna(0.0)

        # Compute a threshold: median * 1.5 (you can tune this later)
        median_footprint = df["carbon_emission"].median() if not df["carbon_emission"].isna().all() else 0.0
        threshold = max(median_footprint * 1.5, 0.1)

        def infer_type(ce):
            try:
                return "non-eco" if ce > threshold else "eco"
            except Exception:
                return "eco"

        df["type"] = df["carbon_emission"].apply(infer_type)

        # --------------------------
        # Heuristic size inference from name/description (small/medium/large)
        # --------------------------
        def infer_size(row):
            text = f"{row.get('name','')} {row.get('description','')}".lower()
            if re.search(r"\b(xl|xxl|large|big|giant|6 ?piece|12 ?litre|12l|25-piece)\b", text):
                return "large"
            if re.search(r"\b(small|mini|pack of 2|pack of 3|single|1pc|1 pack)\b", text):
                return "small"
            return "medium"

        df["size"] = df["size"].fillna(df.apply(infer_size, axis=1))

        # --------------------------
        # Normalize columns that recommender uses
        # --------------------------
        df["category_norm"] = df["category"].astype(str).str.lower().str.strip()
        df["size_norm"] = df["size"].astype(str).str.lower().str.strip()
        df["type_norm"] = df["type"].astype(str).str.lower().str.strip()
        df["name_norm"] = df["name"].astype(str).apply(clean_text)
        df["description_norm"] = df["description"].astype(str).apply(clean_text)

        # Keep DataFrame on self
        self.products = df

    # ----------------------------------------------
    # 🧠 Parse user input (detect product, size, compare)
    # ----------------------------------------------
    def parse_input(self, user_input):
        user_input = clean_text(user_input)
        all_keywords = list(CATEGORY_SYNONYMS.keys())

        # Detect product keywords using fuzzy on whole sentence
        found = [word for word in all_keywords if fuzzy_find(word, [user_input])]
        products = re.findall(r"\b(bag|bottle|brush|cup|straw|plate|comb)\b", user_input)
        if not products and found:
            products = found

        sizes = re.findall(r"\b(small|medium|large)\b", user_input)

        if len(products) >= 2:
            return {"compare": True, "products": products[:2]}
        elif len(products) == 1:
            category = CATEGORY_SYNONYMS.get(products[0], products[0])
            return {"compare": False, "category": category, "size": sizes[0] if sizes else None}
        else:
            # fallback: try to find any product name inside input using fuzzy matching against names
            names = self.products["name"].tolist()
            match = fuzzy_find(user_input, names, threshold=65)
            if match:
                # decide category from matched product
                row = self.products[self.products["name"].str.lower() == match.lower()].iloc[0]
                return {"compare": False, "category": row["category_norm"], "size": row["size_norm"]}
            return {"compare": False}

    # ----------------------------------------------
    # 🌱 Recommend eco alternative
    # ----------------------------------------------
    def recommend(self, user_input):
        parsed = self.parse_input(user_input)
        df = self.products

        if parsed.get("compare"):
            return self.compare_products(parsed["products"][0], parsed["products"][1])

        category = parsed.get("category")
        size = parsed.get("size")
        if not category:
            return {"success": False, "message": "No product detected in your request."}

        # Use category_norm when filtering
        eco_df = df[(df["category_norm"].str.contains(category, na=False)) & (df["type_norm"] == "eco")]
        non_eco_df = df[(df["category_norm"].str.contains(category, na=False)) & (df["type_norm"] == "non-eco")]

        # If size provided, filter
        if size:
            eco_df = eco_df[eco_df["size_norm"] == size]
            non_eco_df = non_eco_df[non_eco_df["size_norm"] == size]

        # If none found, try semantic match on category strings (from categories list)
        if eco_df.empty:
            best_match = semantic_match(category, df["category_norm"].unique().tolist())
            if best_match:
                eco_df = df[(df["category_norm"] == best_match) & (df["type_norm"] == "eco")]
                non_eco_df = df[(df["category_norm"] == best_match) & (df["type_norm"] == "non-eco")]

        if eco_df.empty or non_eco_df.empty:
            return {"success": False, "message": "No eco alternative found for this category.", "parsed": parsed}

        eco_product = eco_df.sort_values("carbon_emission").iloc[0]
        non_eco_product = non_eco_df.sort_values("carbon_emission", ascending=False).iloc[0]

        return {
            "success": True,
            "parsed": parsed,
            "recommended": {
                "id": int(eco_product["id"]),
                "name": eco_product["name"],
                "category": eco_product["category"],
                "material": eco_product.get("material"),
                "size": eco_product["size"],
                "type": eco_product["type"],
                "carbon_emission": float(eco_product["carbon_emission"]),
                "durability_score": int(eco_product.get("durability_score", 0)) if pd.notna(eco_product.get("durability_score")) else None,
                "price": float(eco_product["price"]) if pd.notna(eco_product["price"]) else None,
                "description": eco_product.get("description"),
                "brand": eco_product.get("brand")
            },
            "reason": (
                f"{eco_product['name']} is more eco-friendly with "
                f"{eco_product['carbon_emission']} kg CO₂e compared to "
                f"{non_eco_product['name']} ({non_eco_product['carbon_emission']} kg CO₂e)."
            )
        }

    # ----------------------------------------------
    # ⚖️ Compare two products directly
    # ----------------------------------------------
    def compare_products(self, prod1, prod2):
        df = self.products
        names = df["name"].tolist()

        prod1_match = fuzzy_find(prod1, names, threshold=65) or semantic_match(clean_text(prod1), names)
        prod2_match = fuzzy_find(prod2, names, threshold=65) or semantic_match(clean_text(prod2), names)

        if not prod1_match or not prod2_match:
            return {"success": False, "message": "One or both products not found"}

        p1 = df[df["name"].str.lower() == prod1_match.lower()]
        p2 = df[df["name"].str.lower() == prod2_match.lower()]

        if p1.empty or p2.empty:
            return {"success": False, "message": "One or both products not found"}

        p1 = p1.iloc[0]
        p2 = p2.iloc[0]

        # If the fuzzy match resolved to the same name, try getting eco vs non-eco within same category
        if p1["name"].lower() == p2["name"].lower():
            category = p1["category_norm"]
            eco_variant = df[(df["category_norm"] == category) & (df["type_norm"] == "eco")]
            non_eco_variant = df[(df["category_norm"] == category) & (df["type_norm"] == "non-eco")]
            if not eco_variant.empty and not non_eco_variant.empty:
                p1 = eco_variant.iloc[0]
                p2 = non_eco_variant.iloc[0]
            else:
                # fallback — keep the original items
                pass

        better = p1 if p1["carbon_emission"] < p2["carbon_emission"] else p2
        worse = p2 if better is p1 else p1

        return {
            "success": True,
            "recommended": {
                "id": int(better["id"]),
                "name": better["name"],
                "category": better["category"],
                "carbon_emission": float(better["carbon_emission"]),
                "price": float(better["price"]) if pd.notna(better["price"]) else None
            },
            "reason": (
                f"{better['name']} is more eco-friendly with {better['carbon_emission']} kg CO₂e "
                f"compared to {worse['name']} ({worse['carbon_emission']} kg CO₂e)."
            )
        }

# ==============================================
# 🧪 Self-test (optional)
# ==============================================
if __name__ == "__main__":
    r = Recommender()
    print(r.recommend("recommend a small bag"))
    print(r.recommend("compare eco bag and plastic bag"))
