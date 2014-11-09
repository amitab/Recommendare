from pymongo import MongoClient
from usersimilarity import UserSimilarity

client = MongoClient('localhost', 27017)
db = client.hypertarget_ads

sim = UserSimilarity(db)
sim.dump_similarity_matrix()
