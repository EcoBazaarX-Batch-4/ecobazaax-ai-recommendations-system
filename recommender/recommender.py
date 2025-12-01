import pandas as pd
from rapidfuzz import process, fuzz
# FIX: Import the standalone function
from backend_client.api_client import get_all_products 

class EcoRecommender:
    def __init__(self):
        self.df = None
        self.refresh_data()

    def refresh_data(self):
        """Load products from Spring Boot API into Pandas DataFrame"""
        products = get_all_products()
        if products:
            self.df = pd.DataFrame(products)
            # Ensure columns exist
            required_cols = ['id', 'name', 'categoryName', 'cradleToWarehouseFootprint', 'price']
            for col in required_cols:
                if col not in self.df.columns:
                    self.df[col] = None
            
            # Normalize for matching
            if 'name' in self.df.columns:
                self.df['name_lower'] = self.df['name'].str.lower()
        else:
            self.df = pd.DataFrame()

    def recommend(self, user_query):
        if self.df.empty:
            self.refresh_data()
            if self.df.empty:
                return "I'm having trouble connecting to the product catalog right now."

        # 1. Fuzzy Match
        query_lower = user_query.lower()
        if 'name_lower' not in self.df.columns: return "Catalog empty."
        
        names = self.df['name_lower'].tolist()
        
        # Extract best matches
        matches = process.extract(query_lower, names, scorer=fuzz.WRatio, limit=5)
        relevant_indices = [index for name, score, index in matches if score > 50]

        if not relevant_indices:
            return f"I couldn't find anything like '{user_query}'. Try searching for 'shirt', 'bottle', or 'bag'."

        # 2. Filter & Sort by Eco-Friendliness
        results = self.df.iloc[relevant_indices].copy()
        
        # Sort by Carbon Footprint (Ascending = Better)
        results.sort_values(by='cradleToWarehouseFootprint', ascending=True, na_position='last', inplace=True)
        
        top_pick = results.iloc[0]
        
        response = f"Here is the most eco-friendly option I found:\n\n"
        response += f"🌿 **{top_pick['name']}**\n"
        response += f"💰 Price: ₹{top_pick['price']}\n"
        response += f"🌍 Carbon: {top_pick['cradleToWarehouseFootprint']} kg CO₂e\n"
        
        if len(results) > 1:
            runner_up = results.iloc[1]
            response += f"\nAlso consider: {runner_up['name']} ({runner_up['cradleToWarehouseFootprint']} kg)"
            
        return response