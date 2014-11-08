import math
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.hypertarget_ads

def change_range(OldValue, OldMax, OldMin, NewMax, NewMin):
    OldRange = (OldMax - OldMin)
    if OldRange == 0:
        NewValue = NewMin
    else:
        NewRange = (NewMax - NewMin)  
        NewValue = (((OldValue - OldMin) * NewRange) / float(OldRange)) + NewMin
    
    return NewValue

def cosine_sim(vector_x, vector_y):
    
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

def build_user_vectors(user1, user2):
    
    max_age = db.users.find_one({}, {'age': 1, '_id': 0}, sort=[("age", -1)])['age']
    
    vector_x = [ change_range(user1['age'], max_age, 0, 1, 0) ]
    vector_y = [ change_range(user2['age'], max_age, 0, 1, 0) ]
    
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

def get_user_similarity(user1, user2):
    
    vectors = build_user_vectors(user1, user2)
    return cosine_sim(vectors['user1'], vectors['user2'])
    
user1 = db.users.find_one({'id': 479})
user2 = db.users.find_one({'id': 486})

print get_user_similarity(user1, user2)