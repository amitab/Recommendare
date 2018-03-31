from pymongo import MongoClient
import common

class MovieWrapper(object):
    def get_movie_details(self, movie_id):
        return common.movies.find_one({'id': int(movie_id)}, {'_id': 0})

    def get_next_id(self):
        max_id = common.movies.find({},{'id':1, '_id':0}).sort([('id', -1)]).limit(1)[0]['id']
        return int(max_id) + 1