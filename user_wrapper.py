import time
import common

class UserWrapper(object):
    def get_user(self, user_id):
        user_id = int(user_id)
        user = common.users.find_one({'id': user_id}, {'_id': 0})
        return user

    def get_user_vector(self, user):
        vector = [self.normalize(user['age'], common.user_age_range['max'], common.user_age_range['min'], 1, 0)]
        vector.extend([1 if x == user['sex'] else 0 for x in common.metadata['genders']])
        vector.extend([1 if x == user['occupation'] else 0 for x in common.metadata['occupations']])
        vector.extend([1 if x in user['likes'] else 0 for x in common.metadata['genres']])
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
        max_id = common.users.find({},{'id':1, '_id':0}).sort([('id', -1)]).limit(1)[0]['id']
        return int(max_id) + 1

    def register_user(self, data):
        user = {
            'age': data['age'],
            'sex': data['sex'],
            'occupation': data['occupation'],
            'id': self.get_next_id(),
            'zip_code': data['zip_code'],
            'likes': data.get('likes', [])
        }
        common.users.insert(user)
        return data

    def rate_movie(self, user_id, movie_id, rating):
        new_rating = {
            'rating': rating,
            'timestamp': time.time()
        }
        key = 'ratings.' + str(movie_id)
        scommon.users.update({'id': user_id}, {'$set': {key: new_rating}})
        return

    def get_user_rating_for(self, user_id, movie_id):
        rating = common.users.find_one({'id': user_id}, {'_id': 0})['ratings']
        return rating[movie_id]['rating']

    def get_user_movies(self, user_id, rating = None):
        movies = []
        ratings = common.users.find_one({'id': user_id}, {'_id': 0})['ratings']
        for movie_id in ratings.keys():
            if rating != None:
                if ratings[movie_id]['rating'] >= rating:
                    movies.append(movie_id)
            else:
                movies.append(movie_id)
        return movies
