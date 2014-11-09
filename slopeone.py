import pyprind
import json

class SlopeOne:
    
    def __init__(self, db):
        self.deviation_matrix = {}
        self.db = db
    
    def deviation(self, item1, item2):
        # finding common users who rated the movie
        keys = list(set(item1.keys()) & set(item2.keys()))
        
        deviation = 0
        card_x_y = len(keys)
        
        for key in keys:
            num = item1[key] - item2[key]
            deviation += num / float(card_x_y)

        return {
            'deviation': deviation,
            'cardinality': card_x_y
        }
    
    def get_movie_vectors(self):
        
        user_count = self.db.users.count()
        print "Preparing movie vectors ( user count: %d )" % (user_count)
        movies = {}
        
        my_prbar = pyprind.ProgBar(user_count)
        
        for user in self.db.users.find():
            for movie in user['ratings']:
                if not movie in movies.keys():
                    movies[movie] = {}
                movies[movie][user['id']] = user['ratings'][movie]['rating']
            my_prbar.update()
        return movies
    
    def calculate_deviation_matrix(self):
        
        deviation_matrix = {}
        movies = self.get_movie_vectors()
        
        print "Calculating deviation matrix ( movies count: %d )" % (len(movies))
        
        my_prbar = pyprind.ProgBar(len(movies))
        
        for i in movies:
            deviation_matrix[i] = {
                'movie_id': i,
                'deviations': {}
            }
            for j in movies:
                if i != j:
                    deviation_matrix[i]['deviations'][j] = self.deviation(movies[i], movies[j])
            my_prbar.update()
        
        self.deviation_matrix = deviation_matrix
        
    def dump_deviation_matrix(self):
        if len(self.deviation_matrix) == 0:
            self.calculate_deviation_matrix()
        with open('data/deviation.json', 'w') as outfile:
            json.dump(self.deviation_matrix.values(), outfile)
        print "deviation.json written to data/deviation.json"
        
        # sudo mongoimport --db hypertarget_ads --collection deviations --type json --file deviation.json --jsonArray