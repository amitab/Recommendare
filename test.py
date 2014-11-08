from autoloader import Helper, Prediction, SimilarityMeasure
from pymongo import MongoClient

import math

client = MongoClient('localhost', 27017)
db = client.hypertarget_ads

def get_user_similarity(user1, user2):
    max_age = db.users.find_one({}, {'age': 1, '_id': 0}, sort=[("age", -1)])['age']
    vectors = Helper.build_user_vectors(user1, user2, max_age)
    return SimilarityMeasure.cosine_similarity(vectors['user1'], vectors['user2'])
    
user1 = db.users.find_one({'id': 479})
user2 = db.users.find_one({'id': 486})

print get_user_similarity(user1, user2)