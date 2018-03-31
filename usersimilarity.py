import math
import pyprind
import json
from pymongo import MongoClient
import config
from user_wrapper import UserWrapper
import similarity

class UserSimilarity:
    def __init__(self, db = None):
        if db == None:
            client = MongoClient(config.db_config['host'], config.db_config['port'])
            self.db = client.recommender
        else:
            self.db = db
            
        self.user_interface = UserWrapper(self.db)
        self.user_similarity_matrix = {}
        self.genres = config.genres_list

    def find_users_similarity(self, user1, user2):
        x = self.user_interface.get_user_vector(user1)
        y = self.user_interface.get_user_vector(user2)
        return similarity.cosine_similarity(x, y)

    def find_similar_users(self, user_id = None, user = None):
        if user_id != None:
            current_user = self.db.users.find_one({'id': user_id}, {'_id': 0})
        else:
            current_user = user

        similar_users = []
        for user in self.db.users.find():
            if user['id'] != user_id:
                similar_users.append({
                    'user_id': user['id'],
                    'similarity': self.find_users_similarity(current_user, user)
                })

        return similar_users

    def update_user_similarity(self, user_data):
        similarity = self.find_similar_users(user = user_data)
        similarity_obj = {'user_id': user_data['id'], 'similarity': similarity}

        # create a new similarity list for this guy
        self.db.user_similarity.insert(similarity_obj)
        key = 'similarity.' + str(user_data['id'])

        # update this persons similarity in the lists of all the other users
        for user in similarity:
            self.db.user_similarity.update({'user_id': user}, {'$set': {key : similarity[user]}})

    def find_k_nearest(self, user_id, k):
        return [
            x['similarity'] for x in
            self.db.user_similarity.aggregate([
                { '$match': { 'user_id': user_id } },
                { '$unwind': '$similarity' },
                { '$sort': {'similarity.similarity': -1} },
                { '$limit': k },
                { '$project': {'similarity':1, '_id': 0} }
            ])
        ]

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
        data = self.db.users.find_one({'id': user_id}, {'_id': 0})
        likes = list(set(data['likes'] + likes))
        self.db.users.update_one({'id': user_id}, {'$set': {'likes': likes }})
        self.update_user_similarity(data)

# All methods below are batch methods

    def build_user_similarity(self):
        user_count = self.db.users.count()
        print "Preparing user similarity matrix ( user count: %d )" % (user_count)

        my_prbar = pyprind.ProgBar(user_count)

        for user in self.db.users.find():

            self.user_similarity_matrix[user['id']] = {
                'user_id': user['id'],
                'similarity': self.find_similar_users(user_id = user['id'])
            }
            my_prbar.update()

    def get_similarity_matrix(self):
        if len(self.user_similarity_matrix) == 0:
            self.build_user_similarity()
        return self.user_similarity_matrix.values()

    def dump_similarity_matrix(self, path):
        if len(self.user_similarity_matrix) == 0:
            self.build_user_similarity()
            with open(path, 'w') as outfile:
                json.dump(self.user_similarity_matrix.values(), outfile)
                print "user_similarity.json written to {}".format(path)

        # sudo mongoimport --db hypertarget_ads --collection user_similarity --type json --file user_similarity.json --jsonArray