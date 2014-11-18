import time

from pymongo import MongoClient
from operator import itemgetter, attrgetter, methodcaller

from usersimilarity import UserSimilarity
from slopeone import SlopeOne

class Recommendare:
    
    def __init__(self, db = None):
        if db is None:
            client = MongoClient('localhost', 27017)
            self.db = client.hypertarget_ads
        else:
            self.db = db
            
        self.user_similarity = UserSimilarity(self.db)
        self.slope_one = SlopeOne(self.db)
        
    def rate_neighbours_movies(self, user_id):
        neighbours = self.user_similarity.get_neighbours_movies(user_id)
        movies_list = {}
        
        for index, neighbour in enumerate(neighbours):
            movies = neighbours[index]['movies']
            
            for movie in movies:
                #neighbours[index]['movies'][movie] = self.slope_one.predict_rating(user_id, int(movie))
                if not movie in movies_list.keys():
                    movies_list[movie] = {
                        'slope_rating': self.slope_one.predict_rating(user_id, int(movie)),
                        'neighbours': []
                    }
                    
                movies_list[movie]['neighbours'].append({
                    'neighbour_id': neighbours[index]['user_id'],
                    'neighbour_rating': self.user_similarity.get_user_rating_for(neighbours[index]['user_id'], movie),
                    'neighbour_similarity': neighbours[index]['similarity']
                })
                
        return movies_list
        
    def recommend(self, user_id):
        movies_list = self.rate_neighbours_movies(user_id)
        recommendations = []
        
        for movie in movies_list:
            num = movies_list[movie]['slope_rating']
            den = 1
            
            for neighbour in movies_list[movie]['neighbours']:
                num += neighbour['neighbour_similarity'] * neighbour['neighbour_rating']
                den += neighbour['neighbour_similarity']
            
                recommendations.append((movie, num / float(den)))
                
            
        return sorted(recommendations, key = itemgetter(1), reverse = True)
    
    def get_next_id(self):
        max_id = self.db.users.find({},{'id':1, '_id':0}).sort([('id', -1)]).limit(1)[0]['id']
        return int(max_id) + 1
    
    def register_user(self, data):
        user = {
            'ratings': {},
            'age': data['age'],
            'sex': data['sex'],
            'occupation': data['occupation'],
            'id': self.get_next_id(),
            'zip_code': data['zip_code']
        }
        
        self.db.users.insert(user)
        
        
    def rate_movie(self, data):
        new_rating = {
            'rating': data['rating'],
            'timestamp': time.time()
        }
        key = 'rating.' + str(data['movie_id'])
        self.db.users.update({'id': data['user_id']}, {'$set': {key: new_rating}})
        
        self.slope_one.update_deviation(data)
        return