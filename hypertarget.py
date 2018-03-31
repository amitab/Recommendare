from pymongo import MongoClient
from operator import itemgetter, attrgetter, methodcaller

import config
from Recommendare import Recommendare
from movie_wrapper import MovieWrapper
from usersimilarity import UserSimilarity
from user_wrapper import UserWrapper

class Hypertarget:

    def __init__(self, db = None):
        if db == None:
            client = MongoClient(config.db_config['host'], config.db_config['port'])
            self.db = client.recommender
        else:
            self.db = db

        self.recommender = Recommendare(self.db)
        self.movie_wrapper = MovieWrapper(self.db)
        self.similarity = UserSimilarity(self.db)
        self.user_wrapper = UserWrapper(self.db)

    def hypertarget(self, user_id, count, knn=3):
        movie_set = self.recommender.recommend(user_id, count, knn)
        movies = []

        for movie in movie_set:
            movies.append({
                'predicted_rating': movie[1],
                'movie_id': movie[0],
                #'details': self.movie_wrapper.get_movie_details(movie[0])
            })

        return movies

    def register_user(self, user_data):
        self.similarity.register_user(user_data)

    def update_user_like(self, user_id, likes):
        self.similarity.update_user_likes(user_id, likes)

    def user_rate_movie(self, user_id, movie_id, rating):
        self.recommender.slope_one.update_deviation(user_id, movie_id, rating)
        self.user_wrapper.rate_movie(user_id, movie_id, rating)

h = Hypertarget()
print h.hypertarget(1, 10)