import math
import pyprind
import json

class UserSimilarity:
    
    def __init__(self, db):
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
        
    def change_range(self, OldValue, OldMax, OldMin, NewMax, NewMin):
        OldRange = (OldMax - OldMin)
        if OldRange == 0:
            NewValue = NewMin
        else:
            NewRange = (NewMax - NewMin)  
            NewValue = (((OldValue - OldMin) * NewRange) / float(OldRange)) + NewMin

        return NewValue

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
    
    def find_similar_users(self, user_id):
        current_user = self.db.users.find_one({'id': user_id}, {'_id': 0})
        similar_users = {}
        for user in self.db.users.find():
            if user['id'] != user_id:
                similar_users[user['id']] = self.find_users_similarity(current_user, user)
                
        return similar_users

    def build_user_similarity(self):
        
        user_count = self.db.users.count()
        print "Preparing user similarity matrix ( user count: %d )" % (user_count)
        
        my_prbar = pyprind.ProgBar(user_count)
        
        for user in self.db.users.find():
            
            self.user_similarity_matrix[user['id']] = {
                'user_id': user['id'],
                'similarity': self.find_similar_users(user['id'])
            }
            my_prbar.update()
            
    def dump_similarity_matrix(self):
        if len(self.user_similarity_matrix) == 0:
            self.build_user_similarity()
        with open('data/user_similarity.json', 'w') as outfile:
            json.dump(self.user_similarity_matrix.values(), outfile)
        print "deviation.json written to data/user_similarity.json"
        
        # sudo mongoimport --db hypertarget_ads --collection user_similarity --type json --file user_similarity.json --jsonArray
        
