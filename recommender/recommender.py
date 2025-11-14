import pandas as pd
import re
import os
from rapidfuzz import fuzz, process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
    """Normalize text for better fuzzy and semantic matching."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'(.)\1{2,}', r'\1', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ==============================================
# 🔍 PHASE 3: Fuzzy & semantic matching
# ==============================================
def fuzzy_find(term, choices, threshold=70):
    """Find closest fuzzy match for a term."""
    match, score, _ = process.extractOne(term, choices, scorer=fuzz.partial_ratio)
    if score >= threshold:
        return match
    return None

def semantic_match(query, choices, top_n=1):
    """Use TF-IDF + cosine similarity for semantic matching."""
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([query] + choices)
    cosine_sim = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
    best_idx = cosine_sim.argsort()[-top_n:][::-1]
    best_matches = [(choices[i], cosine_sim[i]) for i in best_idx]
    if best_matches and best_matches[0][1] > 0.3:
        return best_matches[0][0]
    return None

# ==============================================
# 🌿 PHASE 4: Main Recommender class
# ==============================================
class Recommender:
    def __init__(self):
        csv_path = os.path.join(os.path.dirname(__file__), "product_data.csv")
        self.products = pd.read_csv(csv_path)

        # Normalize columns for consistent comparisons
        self.products["category_norm"] = self.products["category"].str.lower().str.strip()
        self.products["size_norm"] = self.products["size"].str.lower().str.strip()
        self.products["type_norm"] = self.products["type"].str.lower().str.strip()
        self.products["name_norm"] = self.products["name"].apply(clean_text)

    # ----------------------------------------------
    # 🧠 Parse user input (detect product, size, compare)
    # ----------------------------------------------
    def parse_input(self, user_input):
        user_input = clean_text(user_input)
        all_keywords = list(CATEGORY_SYNONYMS.keys())

        # Detect known product keywords
        found = [word for word in all_keywords if fuzzy_find(word, [user_input])]
        products = re.findall(r"\b(bag|bottle|brush|cup|straw|plate|comb)\b", user_input)
        if not products and found:
            products = found

        # Extract size terms
        sizes = re.findall(r"\b(small|medium|large)\b", user_input)

        # Identify comparison intent
        if len(products) >= 2:
            return {"compare": True, "products": products[:2]}
        elif len(products) == 1:
            category = CATEGORY_SYNONYMS.get(products[0], products[0])
            return {"compare": False, "category": category, "size": sizes[0] if sizes else None}
        else:
            return {"compare": False}

    # ----------------------------------------------
    # 🌱 Recommend eco alternative
    # ----------------------------------------------
    def recommend(self, user_input):
        parsed = self.parse_input(user_input)
        df = self.products

        # Comparison mode
        if parsed.get("compare"):
            return self.compare_products(parsed["products"][0], parsed["products"][1])

        category = parsed.get("category")
        size = parsed.get("size")
        if not category:
            return {"success": False, "message": "No product detected in your request."}

        # Find matching products
        eco_df = df[(df["category_norm"].str.contains(category, na=False)) & (df["type_norm"] == "eco")]
        non_eco_df = df[(df["category_norm"].str.contains(category, na=False)) & (df["type_norm"] == "non-eco")]

        # Size filtering
        if size:
            eco_df = eco_df[eco_df["size_norm"] == size]
            non_eco_df = non_eco_df[non_eco_df["size_norm"] == size]

        # Try semantic fallback if no match found
        if eco_df.empty:
            best_match = semantic_match(category, df["category_norm"].tolist())
            if best_match:
                eco_df = df[(df["category_norm"] == best_match) & (df["type_norm"] == "eco")]

        if eco_df.empty or non_eco_df.empty:
            return {"success": False, "message": "No eco alternative found for this item.", "parsed": parsed}

        eco_product = eco_df.iloc[0]
        non_eco_product = non_eco_df.iloc[0]

        return {
            "success": True,
            "parsed": parsed,
            "recommended": eco_product.to_dict(),
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

     # Fuzzy match product names
     names = df["name"].tolist()
     prod1_match = fuzzy_find(prod1, names)
     prod2_match = fuzzy_find(prod2, names)

     if not prod1_match or not prod2_match:
         return {"success": False, "message": "One or both products not found"}

     p1 = df[df["name"].str.lower() == prod1_match.lower()]
     p2 = df[df["name"].str.lower() == prod2_match.lower()]

     # 🩵 Handle case when both are same product name (like 'EcoBag' vs 'EcoBag')
     if not p1.empty and not p2.empty and p1.iloc[0]['name'].lower() == p2.iloc[0]['name'].lower():
         category = p1.iloc[0]['category_norm']
         eco_variant = df[(df['category_norm'] == category) & (df['type_norm'] == 'eco')]
         non_eco_variant = df[(df['category_norm'] == category) & (df['type_norm'] == 'non-eco')]
         
         if not eco_variant.empty and not non_eco_variant.empty:
             p1, p2 = eco_variant.iloc[0], non_eco_variant.iloc[0]
         else:
             return {"success": False, "message": "Could not find both eco and non-eco variants for comparison"}
     else:
         if p1.empty or p2.empty:
             return {"success": False, "message": "One or both products not found"}
         p1, p2 = p1.iloc[0], p2.iloc[0]

     # Pick the greener product
     better = p1 if p1['carbon_emission'] < p2['carbon_emission'] else p2
     worse = p2 if better is p1 else p1

     return {
         "success": True,
         "recommended": better.to_dict(),
         "reason": f"{better['name']} is more eco-friendly with {better['carbon_emission']} kg CO₂e compared to {worse['name']} ({worse['carbon_emission']} kg CO₂e)."
     }


# ==============================================
# ✅ PHASE 5: Self-test (Optional)
# ==============================================
if __name__ == "__main__":
    recommender = Recommender()
    print(recommender.recommend("show me eco-friendly bamboo brush"))
    print(recommender.recommend("compare steel bottle and plastic bottle"))
