from pymongo import MongoClient

import config

class MovieWrapper:

    def __init__(self, db = None):
        if db == None:
        
            client = MongoClient(config.db_config['host'], config.db_config['port'])
            self.db = client.hypertarget_ads
        
        else:
            self.db = db
        
        self.config = config.tmdb_config

    def get_movie_details(self, movie_id):
        try:
            movie = self.db.movies.find_one({'id': int(movie_id)}, {'_id': 0})

            if movie['poster_path'] != None:
                movie['images'] = {
                    '92': self.config['images']['base_url'] + 'w92' + movie['poster_path'],
                    '154': self.config['images']['base_url'] + 'w154' + movie['poster_path'],
                    '185': self.config['images']['base_url'] + 'w185' + movie['poster_path'],
                    '342': self.config['images']['base_url'] + 'w342' + movie['poster_path'],
                    '500': self.config['images']['base_url'] + 'w500' + movie['poster_path'],
                    '780': self.config['images']['base_url'] + 'w780' + movie['poster_path'],
                    'original': self.config['images']['base_url'] + 'original' + movie['poster_path']
                }
            else:
                movie['images'] = {}
            return movie
        except:
            return None
