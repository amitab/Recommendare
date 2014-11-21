from pymongo import MongoClient

from usersimilarity import UserSimilarity
from slopeone import SlopeOne

client = MongoClient('localhost', 27017)
db = client.hypertarget_ads

slope = SlopeOne(db)
similarity = UserSimilarity(db)

slope.dump_deviation_matrix()
similarity.dump_similarity_matrix()