import math
import pyprind
import json

from pymongo import MongoClient

import config

class MovieSimilarity:

    def __init__(self, db = None):
        if db == None:
        
            client = MongoClient(config.db_config['host'], config.db_config['port'])
            self.db = client.recommender
        
        else:
            self.db = db
            
        self.movie_similarity_matrix = {}
        self.genres = ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Disaster', 'Documentary', 'Drama', 'Eastern', 'Erotic', 'Family', 'Fan Film', 'Fantasy', 'Film Noir', 'Foreign', 'History', 'Holiday', 'Horror', 'Indie', 'Music', 'Musical', 'Mystery', 'Neo-noir', 'Road Movie', 'Romance', 'Science Fiction', 'Short', 'Sport', 'Sporting Event', 'Sports Film', 'Suspense', 'TV movie', 'Thriller', 'War', 'Western']
            
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
            
    def build_movie_vector(self, movie):
        vector = []
        genres = []
        for genre in movie['genres']:
            genres.append(genre['name'])
            
        for genre in self.genres:
            if genre in genres:
                vector.append(1)
            else:
                vector.append(0)
        
        return vector
        
    def get_similarity(self, movie_1, movie_2):
        vector_x = self.build_movie_vector(movie_1)
        vector_y = self.build_movie_vector(movie_2)
        
        return self.cosine_similarity(vector_x, vector_y)
        
    def find_similar_movies(self, movie_id):
        this_movie = self.db.movies.find_one({'id': movie_id}, {'_id': 0})
        similarity = {}
        
        for movie in self.db.movies.find():
            similarity[movie['id']] = self.get_similarity(this_movie, movie)
        
        return similarity
        
    def build_movie_similarity(self):

        movie_count = self.db.movies.count()
        print "Preparing movie similarity matrix ( movie count: %d )" % (movie_count)

        my_prbar = pyprind.ProgBar(movie_count)

        for movie in self.db.movies.find():

            self.movie_similarity_matrix[movie['id']] = {
                'movie_id': movie['id'],
                'similarity': self.find_similar_movies(movie['id'])
            }
            my_prbar.update()
            
    def dump_similarity_matrix(self):
        if len(self.movie_similarity_matrix) == 0:
            self.build_movie_similarity()
            with open('data/movie_similarity.json', 'w') as outfile:
                json.dump(self.movie_similarity_matrix.values(), outfile)
                print "movie_similarity.json written to data/movie_similarity.json"

        # sudo mongoimport --db hypertarget_ads --collection movie_similarity --type json --file movie_similarity.json --jsonArray
        
ms = MovieSimilarity()
ms.dump_similarity_matrix()
            
