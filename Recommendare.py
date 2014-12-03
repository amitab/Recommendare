import time
from multiprocessing.pool import ThreadPool as Pool
from pymongo import MongoClient
from operator import itemgetter

import config
from usersimilarity import UserSimilarity
from slopeone import SlopeOne

class Recommendare:

    def __init__(self, db = None):
        if db == None:
        
            client = MongoClient(config.db_config['host'], config.db_config['port'])
            self.db = client.hypertarget_ads
        
        else:
            self.db = db

        self.user_similarity = UserSimilarity(self.db)
        self.slope_one = SlopeOne(self.db)

        self.pool = Pool(processes = 10)
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

    def rate_neighbours_movies(self, user_id, count):
        neighbours = self.user_similarity.get_neighbours_movies(user_id, k = 3)
        all_movies = []
        
        for neighbour in neighbours:
            all_movies.append(set(neighbour['movies']))
        
        temp = set.intersection(*all_movies)
        
        if len(temp) >= count:
            all_movies = temp
        else:
            all_movies = set.union(*all_movies)
        
        for neighbour in neighbours:
            for n_movie in neighbour['movies']:
                if n_movie in all_movies:
                    self.pool.apply_async(self.user_prediction, (user_id, n_movie, neighbour))

        self.pool.close()
        self.pool.join()

    def get_recommended_movies(self, user_id, count):
        if len(self.recommended_movies) == 0:
            self.rate_neighbours_movies(user_id, count)
            return self.recommended_movies

    def recommend(self, user_id, count):
        movies_list = self.get_recommended_movies(user_id, count)

        recommendations = []

        for movie in movies_list:
            num = movies_list[movie]['slope_rating']
            den = 1

            for neighbour in movies_list[movie]['neighbours']:
                num += neighbour['neighbour_similarity'] * neighbour['neighbour_rating']
                den += neighbour['neighbour_similarity']

            recommendations.append((movie, num / float(den)))


        return sorted(recommendations, key = itemgetter(1), reverse = True)[:count]
