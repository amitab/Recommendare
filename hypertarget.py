from pymongo import MongoClient
from operator import itemgetter, attrgetter, methodcaller

from Recommendare import Recommendare
from movie_wrapper import MovieWrapper

class Hypertarget:

    def __init__(self, db = None):
        if db is None:
            client = MongoClient('localhost', 27017)
            self.db = client.hypertarget_ads
        else:
            self.db = db

        self.recommender = Recommendare(self.db)
        self.movie_wrapper = MovieWrapper(self.db)

    def hypertarget(self, user_id, count):
        movie_set = self.recommender.recommend(user_id, count)
        movies = []

        for movie in movie_set:
            movies.append({
                'predicted_rating': movie[1],
                'movie_id': movie[0],
                'details': self.movie_wrapper.get_movie_details(movie[0])
            })

        return movies
