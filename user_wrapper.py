from pymongo import MongoClient
import time
import config
from slopeone import SlopeOne

class UserWrapper:
    def __init__(self, db = None):
        if db == None:
            client = MongoClient(config.db_config['host'], config.db_config['port'])
            self.db = client.hypertarget_ads
        else:
            self.db = db

        self.slope_one = SlopeOne(self.db)

        data = self.db.users.aggregate([{
            '$group': {
                '_id': 0,
                'max': {'$max': '$age'},
                'min': {'$min': '$age'}
            } }]).next()
        self.max_user_age, self.min_user_age = data['max'], data['min']

        self.occupations = ['administrator', 'artist', 'doctor', 'educator', 'engineer', 'entertainment', 'executive', 'healthcare', 'homemaker', 'lawyer', 'librarian', 'marketing', 'none', 'other', 'programmer', 'retired', 'salesman', 'scientist', 'student', 'technician', 'writer']
        self.genres = ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Disaster', 'Documentary', 'Drama', 'Eastern', 'Erotic', 'Family', 'Fan Film', 'Fantasy', 'Film Noir', 'Foreign', 'History', 'Holiday', 'Horror', 'Indie', 'Music', 'Musical', 'Mystery', 'Neo-noir', 'Road Movie', 'Romance', 'Science Fiction', 'Short', 'Sport', 'Sporting Event', 'Sports Film', 'Suspense', 'TV movie', 'Thriller', 'War', 'Western']
        self.genders = ['M', 'F']

    def get_user(self, user_id):
        user_id = int(user_id)
        user = self.db.users.find_one({'id': user_id}, {'_id': 0})
        
        return user

    def get_base_user_vector(self):
        user = [1, 1]
        user.extend([1 for x in self.occupations])
        user.extend([1 for x in self.genres])
        return user

    def get_user_vector(self, user):
        vector = [self.normalize(user['age'], self.max_user_age, self.min_user_age, 1, 0)]
        vector.extend([1 if x == user['sex'] else 0 for x in self.genders])
        vector.extend([1 if x == user['occupation'] else 0 for x in self.occupations])
        vector.extend([1 if x in user['likes'] else 0 for x in self.genres])
        return vector

    def normalize(self, old_value, old_max, old_min, new_max, new_min):
        old_range = (old_max - old_min)
        if old_range == 0:
            new_value = new_min
        else:
            new_range = (new_max - new_min)
            new_value = (((old_value - old_min) * new_range) / float(old_range)) + new_min

        return new_value

    def get_next_id(self):
        max_id = self.db.users.find({},{'id':1, '_id':0}).sort([('id', -1)]).limit(1)[0]['id']
        return int(max_id) + 1

    def register_user(self, data):
        user = {
            'age': data['age'],
            'sex': data['sex'],
            'occupation': data['occupation'],
            'id': self.get_next_id(),
            'zip_code': data['zip_code']
        }
        self.db.users.insert(user)

    def rate_movie(self, data):
        self.slope_one.update_deviation(data)
        new_rating = {
            'rating': data['rating'],
            'timestamp': time.time()
        }
        key = 'ratings.' + str(data['movie_id'])
        self.db.users.update({'id': data['user_id']}, {'$set': {key: new_rating}})
        return

    def get_user_rating_for(self, user_id, movie_id):
        rating = self.db.users.find_one({'id': user_id}, {'_id': 0})['ratings']
        return rating[movie_id]['rating']

    def get_user_movies(self, user_id, rating = None):
        movies = []
        ratings = self.db.users.find_one({'id': user_id}, {'_id': 0})['ratings']
        for movie_id in ratings.keys():
            if rating != None:
                if ratings[movie_id]['rating'] >= rating:
                    movies.append(movie_id)
            else:
                movies.append(movie_id)
        return movies
