import pyprind
import json

class SlopeOne:

    def __init__(self, db = None):
        if db != None:
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
                'movie_id': int(i),
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

    def predict_rating(self, user_id, movie_id):
        try:

            user_ratings = self.db.users.find_one({'id': user_id}, {'_id': 0, 'ratings': 1})['ratings']
            movie_deviations = self.db.deviations.find_one({'movie_id': movie_id}, {'_id': 0, 'deviations': 1})['deviations']

            num = 0
            den = 0

            for movie in user_ratings:
                if int(movie) != movie_id:
                    num += (movie_deviations[movie]['deviation'] + user_ratings[movie]['rating']) * movie_deviations[movie]['cardinality']
                    den += movie_deviations[movie]['cardinality']

            if den == 0:
                return 0
            else:
                return num / float(den)

        except:
            return False

    def update_deviation(self, data):
        user_ratings = self.db.users.find_one({'id': data['user_id']}, {'_id': 0})['ratings']
        movie_deviations = self.db.deviations.find_one({'movie_id': data['movie_id']}, {'_id': 0, 'deviations': 1})['deviations']

        for movie in user_ratings:
            card = movie_deviations[movie]['cardinality']
            dev = movie_deviations[movie]['deviation']

            new_dev = ( (card * dev) + (data['rating'] - user_ratings[movie]['rating']) ) / float(card + 1)

            # update
            # for new_movie vs movie = new_dev
            # for movie vs new_movie = -new_dev

            key = 'deviations.' + str(movie)
            self.db.deviations.update({'movie_id': data['movie_id']}, {'$set': {key : {'deviation': new_dev, 'cardinality': card + 1}}})

            key = 'deviations.' + str(data['movie_id'])
            self.db.deviations.update({'movie_id': int(movie)}, {'$set': {key : {'deviation': -new_dev, 'cardinality': card + 1}}})

        return
