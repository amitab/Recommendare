import common
from Recommendare import Recommendare
from movie_wrapper import MovieWrapper
from usersimilarity import UserSimilarity

class Hypertarget:

    def __init__(self):
        self.recommender = Recommendare()
        self.movie_wrapper = MovieWrapper()
        self.similarity = UserSimilarity()

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

    def update_user_likes(self, user_id, likes):
        self.similarity.update_user_likes(user_id, likes)

    def user_rate_movie(self, user_id, movie_id, rating):
        self.recommender.slope_one.update_deviation(user_id, movie_id, rating)
        self.similarity.rate_movie(user_id, movie_id, rating)

h = Hypertarget()
# print h.recommender.serendipity_recommendation(1, 10)
print h.recommender.fast_recommendation(1, 10)
"""
[{'movie_id': 408, 'predicted_rating': 4.863125453226976}, {'movie_id': 479, 'predicted_rating': 4.728977741137675}, {'movie_id': 302, 'predicted_rating': 4.713568020818274}, {'movie_id': 896, 'predicted_rating': 4.711029092488058}, {'movie_id': 483, 'predicted_rating': 4.672735713523753}, {'movie_id': 647, 'predicted_rating': 4.672344240251008}, {'movie_id': 520, 'predicted_rating': 4.664003403933434}, {'movie_id': 525, 'predicted_rating': 4.647112880992495}, {'movie_id': 315, 'predicted_rating': 4.629603490311818}, {'movie_id': 430, 'predicted_rating': 4.6045407158577545}]
"""