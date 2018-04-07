import time
import math
from operator import itemgetter
from collections import defaultdict

import common
from usersimilarity import UserSimilarity
from slopeone import SlopeOne
from user_wrapper import UserWrapper

class Recommendare:
    def __init__(self):
        self.user_similarity = UserSimilarity()
        self.user_interface  = UserWrapper()
        self.slope_one = SlopeOne()

    def _recommend_movies_list(self, user_id, neighbours, movies):
        similarity = {n['user_id']: n['similarity'] for n in neighbours}
        cosine_ratings = defaultdict(lambda: defaultdict(lambda: 0))
        for m in movies:
            cosine_ratings[m['movie_id']]['num'] += similarity[m['user_id']] * m['rating']
            cosine_ratings[m['movie_id']]['den'] += similarity[m['user_id']]
        return [{
            'movie_id': p['movie_id'],
            'predicted_rating': (p['rating'] + (cosine_ratings[p['movie_id']]['num']/cosine_ratings[p['movie_id']]['den']))/float(2)
        } for p in self.slope_one.predict_ratings(user_id, movies)]

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
        users = common.users.aggregate([{
            '$match': {
                'ratings.movie_id': 1,
                'id': {
                '$ne': 344
                }
            }
            }, {
            '$lookup': {
                'from': 'user_similarity',
                'localField': 'id',
                'foreignField': 'user_id',
                'as': 'similarity'
            }
            }, {
            '$project': {
                '_id': 0,
                'id': 1,
                'rating': {
                '$let': {
                    'vars': {
                    'rr': {
                        '$arrayElemAt': [{
                        '$filter': {
                            'input': '$ratings',
                            'as': 'rating',
                            'cond': {
                            '$eq': ['$$rating.movie_id', 1]
                            }
                        }
                        }, 0]
                    }
                    },
                    'in': '$$rr.rating'
                }
                },
                'similarity': {
                '$let': {
                    'vars': {
                    'kk': {
                        '$let': {
                        'vars': {
                            'similarity': {
                            '$arrayElemAt': ["$similarity", 0]
                            }
                        },
                        'in': {
                            '$arrayElemAt': [{
                            '$filter': {
                                'input': '$$similarity.similarity',
                                'as': 'sim',
                                'cond': {
                                '$eq': ['$$sim.user_id', 344]
                                }
                            }
                            }, 0]
                        }
                        }
                    }
                    },
                    'in': '$$kk.similarity'
                }
                }
            }
            }, {
            '$sort': {
                'similarity': -1
            }
            }, {
            '$limit': 5}])
        slope = self.slope_one.predict_rating(user_id, movie_id)
        den = 0.0
        num = 0
        for user in users:
            den += user['similarity']
            num += user['rating'] * user['similarity']
        if den == 0.0:
            return slope
        return ((num / den) + slope) / 2

    def register_user(self, user_data):
        self.user_similarity.register_user(user_data)

    def update_user_likes(self, user_id, likes):
        self.self.user_similarity.update_user_likes(user_id, likes)

    def user_rate_movie(self, user_id, movie_id, rating):
        self.slope_one.update_deviation(user_id, movie_id, rating)
        self.user_similarity.rate_movie(user_id, movie_id, rating)