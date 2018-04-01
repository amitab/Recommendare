import time
import math
from operator import itemgetter

import common
from usersimilarity import UserSimilarity
from slopeone import SlopeOne
from user_wrapper import UserWrapper

class Recommendare:
    def __init__(self):
        self.user_similarity = UserSimilarity()
        self.user_interface  = UserWrapper()
        self.slope_one = SlopeOne()

        self.recommended_movies = {}

    def serendipity_recommendation(self, user_id, count, knn=3):
        neighbours = self.user_similarity.find_k_nearest(user_id, knn)
        movies = list(common.users.aggregate([
            {'$match': {'id': {'$in': [x['user_id'] for x in neighbours]}}},
            {'$unwind': '$ratings'},
            {'$sort': {'ratings.rating': -1}},
            {'$limit': count * 10},
            {'$sample': {'size': count}},
            {'$project': {'_id': 0, 'movie_id': '$ratings.movie_id', 'rating': '$ratings.rating', 'user_id': '$id'}}
        ]))

        return self._recommend_movies_list(user_id, neighbours, movies)

    def _recommend_movies_list(self, user_id, neighbours, movies):
        similarity = {n['user_id']: n['similarity'] for n in neighbours}
        cosine_ratings = {m['movie_id'] : similarity[m['user_id']] * m['rating'] for m in movies}
        return [{
            'movie_id': p['movie_id'],
            'predicted_rating': (p['rating'] + cosine_ratings[p['movie_id']])/2
        } for p in self.slope_one.predict_ratings(user_id, movies)]

    def best_recommendation(self, user_id, count, knn=3):
        neighbours = self.user_similarity.find_k_nearest(user_id, knn)
        movies = list(common.users.aggregate([
            {'$match': {'id': {'$in': [x['user_id'] for x in neighbours]}}},
            {'$unwind': '$ratings'},
            {'$sort': {'ratings.rating': -1}},
            {'$project': {'_id': 0, 'movie_id': '$ratings.movie_id', 'rating': '$ratings.rating', 'user_id': '$id'}}
        ]))
        return sorted(self._recommend_movies_list(user_id, neighbours, movies), key=itemgetter('predicted_rating'), reverse=True)[:count]

    def fast_recommendation(self, user_id, count, knn=3):
        slicer = math.ceil(count/float(knn))
        neighbours = self.user_similarity.find_k_nearest(user_id, knn)
        movies = list(common.users.aggregate([
            {'$project': {'ratings': {'$slice': ['$ratings', slicer]}, 'id': 1}},
            {'$match': {'id': {'$in': [x['user_id'] for x in neighbours]}}},
            {'$unwind': '$ratings'},
            {'$sort': {'ratings.rating': -1}},
            {'$project': {'_id': 0, 'movie_id': '$ratings.movie_id', 'rating': '$ratings.rating', 'user_id': '$id'}}
        ]))
        return sorted(self._recommend_movies_list(user_id, neighbours, movies), key=itemgetter('predicted_rating'), reverse=True)[:count]

    def predict_rating(self, user_id, movie_id, knn=3):
        pass
