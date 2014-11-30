import time
from multiprocessing.pool import ThreadPool as Pool

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
        
        self.pool = Pool(processes = 15)
        self.recommended_movies = {}
    
    def user_prediction(self, user_id, movie, neighbour):
        if not movie in self.recommended_movies.keys():
            self.recommended_movies[movie] = {
                'slope_rating': self.slope_one.predict_rating(user_id, int(movie)),
                'neighbours': []
            }
            
        self.recommended_movies[movie]['neighbours'].append({
            'neighbour_id': neighbour['user_id'],
            'neighbour_rating': self.user_similarity.get_user_rating_for(neighbour['user_id'], movie),
            'neighbour_similarity': neighbour['similarity']
        })
       
    def rate_neighbours_movies(self, user_id):
        neighbours = self.user_similarity.get_neighbours_movies(user_id)
        
        for index, neighbour in enumerate(neighbours):
            movies = neighbours[index]['movies']
            
            for movie in movies:
                self.pool.apply_async(self.user_prediction, (user_id, movie, neighbour))
                
        self.pool.close()
        self.pool.join()
                
    def get_recommended_movies(self, user_id):
        if len(self.recommended_movies) == 0:
            self.rate_neighbours_movies(user_id)
        return self.recommended_movies
        
    def recommend(self, user_id):
        movies_list = self.get_recommended_movies(user_id)
        
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
            'age': data['age'],
            'sex': data['sex'],
            'occupation': data['occupation'],
            'id': self.get_next_id(),
            'zip_code': data['zip_code']
        }
        
        self.db.users.insert(user)
        self.user_similarity.update_user_similarity(user)
        
        return
        
        
    def rate_movie(self, data):
        new_rating = {
            'rating': data['rating'],
            'timestamp': time.time()
        }
        key = 'rating.' + str(data['movie_id'])
        self.db.users.update({'id': data['user_id']}, {'$set': {key: new_rating}})
        
        self.slope_one.update_deviation(data)
        return
