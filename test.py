from pymongo import MongoClient
from usersimilarity import UserSimilarity
from slopeone import SlopeOne

client = MongoClient('localhost', 27017)
db = client.hypertarget_ads

"""
sim = UserSimilarity(db)
#sim.dump_similarity_matrix()
print sim.get_neighbours_movies(479)
"""

slope = SlopeOne(db)
print slope.predict_rating(479, 523)


"""
slope = SlopeOne(db)
slope.dump_deviation_matrix()
"""