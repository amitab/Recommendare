import math
import pyprind
import json

from pymongo import MongoClient

import config

class UserSimilarity:

    def __init__(self, db = None):
        if db == None:
        
            client = MongoClient(config.db_config['host'], config.db_config['port'])
            self.db = client.hypertarget_ads
        
        else:
            self.db = db
            
        self.max_user_age = self.db.users.find_one({}, {'age': 1, '_id': 0}, sort=[("age", -1)])['age']
        self.user_similarity_matrix = {}

    def cosine_similarity(self, vector_x, vector_y):
        dot_pdt = 0
        length_x = 0
        length_y = 0

        for i in range(len(vector_x)):
            dot_pdt += vector_x[i] * vector_y[i]
            length_x += vector_x[i] ** 2
            length_y += vector_y[i] ** 2

        length_x = math.sqrt(length_x)
        length_y = math.sqrt(length_y)
        den = length_x * length_y

        if den == 0:
            return 0
        else:
            return dot_pdt / float(den)

    def change_range(self, old_value, old_max, old_min, new_max, new_min):
        old_range = (old_max - old_min)
        if old_range == 0:
            new_value = new_min
        else:
            new_range = (new_max - new_min)
            new_value = (((old_value - old_min) * new_range) / float(old_range)) + new_min

        return new_value

    def build_user_vectors(self, user1, user2):

        vector_x = [ self.change_range(user1['age'], self.max_user_age, 0, 1, 0) ]
        vector_y = [ self.change_range(user2['age'], self.max_user_age, 0, 1, 0) ]

        if user1['sex'] == user2['sex']:
            vector_x.extend([1, 0])
            vector_y.extend([1, 0])
        else:
            vector_x.extend([0, 1])
            vector_y.extend([1, 0])

        if user1['zip_code'] == user2['zip_code']:
            vector_x.extend([1, 0])
            vector_y.extend([1, 0])
        else:
            vector_x.extend([0, 1])
            vector_y.extend([1, 0])

        if user1['occupation'] == user2['occupation']:
            vector_x.extend([1, 0])
            vector_y.extend([1, 0])
        else:
            vector_x.extend([0, 1])
            vector_y.extend([1, 0])

        return {
            'user1': vector_x,
            'user2': vector_y
        }

    def find_users_similarity(self, user1, user2):
        users = self.build_user_vectors(user1, user2)
        return self.cosine_similarity(users['user1'], users['user2'])

    def find_similar_users(self, user_id = None, user = None):
        if user_id != None:
            current_user = self.db.users.find_one({'id': user_id}, {'_id': 0})
        else:
            current_user = user

        similar_users = {}
        for user in self.db.users.find():
            if user['id'] != user_id:
                similar_users[str(user['id'])] = self.find_users_similarity(current_user, user)

        return similar_users

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

    def update_user_similarity(self, user_data):

        similarity = self.find_similar_users(user = user_data)
        similarity_obj = {'user_id': user_data['id'], 'similarity': similarity}

        # create a new similarity list for this guy
        self.db.user_similarity.insert(similarity_obj)
        key = 'similarity.' + str(user_data['id'])

        # update this persons similarity in the lists of all the other users
        for user in similarity:
            self.db.user_similarity.update({'user_id': user}, {'$set': {key : similarity[user]}})


    def dump_similarity_matrix(self):
        if len(self.user_similarity_matrix) == 0:
            self.build_user_similarity()
            with open('data/user_similarity.json', 'w') as outfile:
                json.dump(self.user_similarity_matrix.values(), outfile)
                print "user_similarity.json written to data/user_similarity.json"

        # sudo mongoimport --db hypertarget_ads --collection user_similarity --type json --file user_similarity.json --jsonArray

    def find_k_nearest(self, user_id, k):
        try:
            similarity = self.db.user_similarity.find_one({'user_id': user_id}, {'_id': 0, 'similarity': 1})['similarity']
            neighbours = []
            for key, value in sorted(similarity.items(), key = lambda x:x[1], reverse = True)[:k]:
                neighbours.append({
                    'user_id': int(key),
                    'similarity': value
                })
                # print str(key) + " " + str(value)
            return neighbours
        except:
            return False

    def get_user_movies(self, user_id):
        movies = []
        ratings = self.db.users.find_one({'id': user_id}, {'_id': 0})['ratings']
        for movie_id in ratings.keys():
            movies.append(movie_id)

        return movies

    def get_neighbours_movies(self, user_id, k = 3):

        neighbours = self.find_k_nearest(user_id, k)
        movies = self.get_user_movies(user_id)
        for index, neighbour in enumerate(neighbours):
            neighbours[index]['movies'] = self.get_user_movies(neighbours[index]['user_id'])
            neighbours[index]['movies'] = list(set(neighbours[index]['movies']).difference(set(movies)))

        return neighbours

    def get_user_rating_for(self, user_id, movie_id):

        rating = self.db.users.find_one({'id': user_id}, {'_id': 0})['ratings']
        return rating[movie_id]['rating']
