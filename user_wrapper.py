from pymongo import MongoClient
import time

import config

from usersimilarity import UserSimilarity
from slopeone import SlopeOne

class UserWrapper:

    def __init__(self, db = None):
        if db == None:
        
            client = MongoClient(config.db_config['host'], config.db_config['port'])
            self.db = client.hypertarget_ads
        
        else:
            self.db = db
            
        self.user_similarity = UserSimilarity(self.db)
        self.slope_one = SlopeOne(self.db)

    def get_user(self, user_id):
        
        user_id = int(user_id)
        user = self.db.users.find_one({'id': user_id}, {'_id': 0})
        
        return user    

    def get_next_id(self):
        max_id = self.db.users.find({},{'id':1, '_id':0}).sort([('id', -1)]).limit(1)[0]['id']
        return int(max_id) + 1

    def register_user(self, data):
    
        
        user = {
            'age': data['age'],
            'sex': data['sex'],
            'occupation': data['occupation'],
            'id': self.get_next_id(),
            'zip_code': data['zip_code']
        }
        
        self.user_similarity.update_user_similarity(user)

        self.db.users.insert(user)

        return


    def rate_movie(self, data):

        self.slope_one.update_deviation(data)
        
        new_rating = {
            'rating': data['rating'],
            'timestamp': time.time()
        }
        key = 'ratings.' + str(data['movie_id'])
        self.db.users.update({'id': data['user_id']}, {'$set': {key: new_rating}})
        
        return
