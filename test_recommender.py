# Existing imports
from recommender.recommender import Recommender

r = Recommender()

print("----- Comparison Test -----")
print(r.recommend("which is more eco friendly, eco bag or plastic bag?"))

print("\n----- Suggest Bottle Test -----")
print(r.recommend("suggest an eco friendly bottle"))
