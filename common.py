import json

from pymongo import MongoClient

config = json.load(open('.config'))
tmdb_key = config['tmdb_api_key']
client = MongoClient(config['host'], config['port'])
database = client[config['database']]

meta = database[config['collections']['meta']]
users = database[config['collections']['users']]
movies = database[config['collections']['movies']]
user_similarity = database[config['collections']['user_similarity']]
deviations = database[config['collections']['deviations']]

metadata = meta.find({}, {'_id': 0, 'zip_codes': 0}).next()
user_age_range = users.aggregate([{
    '$group': {
        '_id': 0,
        'max': {'$max': '$age'},
        'min': {'$min': '$age'}
    } }]).next()

def normalize(old_value, old_max, old_min, new_max, new_min):
    old_range = (old_max - old_min)
    if old_range == 0:
        new_value = new_min
    else:
        new_range = (new_max - new_min)
        new_value = (((old_value - old_min) * new_range) / float(old_range)) + new_min

    return new_value