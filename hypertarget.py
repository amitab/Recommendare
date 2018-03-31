from pymongo import MongoClient
from operator import itemgetter, attrgetter, methodcaller

import config
from Recommendare import Recommendare
from movie_wrapper import MovieWrapper

class Hypertarget:

    def __init__(self, db = None):
        if db == None:
            client = MongoClient(config.db_config['host'], config.db_config['port'])
            self.db = client.hypertarget_ads
        else:
            self.db = db

        self.recommender = Recommendare(self.db)
        self.movie_wrapper = MovieWrapper(self.db)

    def hypertarget(self, user_id, count, knn=3):
        movie_set = self.recommender.recommend(user_id, count, knn)
        movies = []

        for movie in movie_set:
            movies.append({
                'predicted_rating': movie[1],
                'movie_id': movie[0],
                'details': self.movie_wrapper.get_movie_details(movie[0])
            })

        return movies