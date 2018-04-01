import pyprind

import common
import similarity

from user_wrapper import UserWrapper

class UserSimilarity(object):
    def __init__(self):
        self.user_interface = UserWrapper()

    def find_users_similarity(self, user1, user2):
        x = self.user_interface.get_user_vector(user1)
        y = self.user_interface.get_user_vector(user2)
        return similarity.cosine_similarity(x, y)

    def find_similar_users(self, current_user):
        return [{
            'user_id': user['id'],
            'similarity': self.find_users_similarity(current_user, user)
        } for user in common.users.find() if user['id'] != current_user['id']]

    def update_user_similarity(self, user_data):
        similarity = self.find_similar_users(user_data)
        similarity_obj = {'user_id': user_data['id'], 'similarity': similarity}

        # create a new similarity list for this guy
        common.user_similarity.insert(similarity_obj)
        key = 'similarity.' + str(user_data['id'])

        # update this persons similarity in the lists of all the other users
        for user in similarity:
            common.user_similarity.update({'user_id': user}, {'$set': {key : similarity[user]}})

    def find_k_nearest(self, user_id, k):
        return [
            x['similarity'] for x in
            common.user_similarity.aggregate([
                { '$match': { 'user_id': user_id } },
                { '$unwind': '$similarity' },
                { '$sort': {'similarity.similarity': -1} },
                { '$limit': k },
                { '$project': {'similarity':1, '_id': 0} }
            ])
        ]

    # def find_k_nearest_with_movie(self, user_id, movie_id, k):
    #     users = common.users.find({'ratings.movie_id': movie_id}, {'_id': 0, 'id': 1})
    #     list(common.user_similarity.aggregate([
    #         { '$match': { 'user_id': user_id } },
    #         { '$unwind': '$similarity' },
    #         {'$match': {'similarity.user_id': {'$in': list(users)}}},
    #         { '$sort': {'similarity.similarity': -1} },
    #         { '$limit': k },
    #         { '$project': {'similarity': '$similarity.similarity', 'user_id': '$similarity.user_id', '_id': 0} }
    #     ]))

    def get_neighbours_movies(self, user_id, k = 3):
        neighbours = self.find_k_nearest(user_id, k)
        movies = self.user_interface.get_user_movies(user_id)
        for index, neighbour in enumerate(neighbours):
            neighbours[index]['movies'] = self.user_interface.get_user_movies(neighbours[index]['user_id'], 3)
            neighbours[index]['movies'] = list(set(neighbours[index]['movies']).difference(set(movies)))
        return neighbours

    def register_user(self, data):
        self.update_user_similarity(self.user_interface.register_user(data))

    def update_user_likes(self, user_id, likes):
        data = common.users.find_one({'id': user_id}, {'_id': 0})
        likes = list(set(data['likes'] + likes))
        common.users.update_one({'id': user_id}, {'$set': {'likes': likes }})
        self.update_user_similarity(data)

    def rate_movie(self, user_id, movie_id, rating):
        self.user_interface.rate_movie(user_id, movie_id, rating)
        if rating == 5:
            self.update_user_likes(
                user_id,
                common.movies.find_one({'id': movie_id}, {'_id': 0, 'genres': 1})['genres'])

    # All methods below are batch methods
    def build_user_similarity(self):
        user_count = common.users.count()
        print "Preparing user similarity matrix ( user count: %d )" % (user_count)
        user_similarity_matrix = {}
        my_prbar = pyprind.ProgBar(user_count)

        for user in common.users.find():
            user_similarity_matrix[user['id']] = {
                'user_id': user['id'],
                'similarity': self.find_similar_users(user)
            }
            my_prbar.update()

        return user_similarity_matrix

    def get_similarity_matrix(self):
        return self.build_user_similarity()
