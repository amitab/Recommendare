import pyprind

import common

class SlopeOne(object):
    # Just with item IDs
    def calculate_devation(self, item1, item2):
        data = common.users.find({'$and': [
            {'ratings.{}'.format(item1): {'$exists': True}},
            {'ratings.{}'.format(item2): {'$exists': True}}
        ]}, {'_id': 0, 'ratings': 1})

        num = 0
        den = data.count()
        if den == 0:
            return { 'deviation': 0, 'cardinality': 0 }
        for user in data:
            num += user['ratings'][item1]['rating'] - user['ratings'][item2]['rating']

        return { 'deviation': num / float(den), 'cardinality': den }

    def predict_ratings(self, user_id, neighbour_movies):
        user_ratings = common.users.find_one({'id': user_id}, {'_id': 0, 'ratings': 1})['ratings']
        deviations = common.deviations.find({
            'movie_id': {
                '$in': [m for m in neighbour_movies[n_m] for n_m in neighbour_movies]}
            }, {'_id': 0})

        return {
            d['movie_id']: self._predict_rating(user_id, d['movie_id'], d['deviations'], user_ratings)
            for d in deviations
        }

    def predict_rating(self, user_id, movie_id):
        user_ratings = common.users.find_one({'id': user_id}, {'_id': 0, 'ratings': 1})['ratings']
        movie_deviations = common.deviations.find_one({'movie_id': movie_id}, {'_id': 0, 'deviations': 1})['deviations']

        return self._predict_rating(user_id, movie_id, movie_deviations, user_ratings)

    def _predict_rating(self, user_id, movie_id, movie_deviations, user_ratings):
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

    def update_deviation(self, user_id, movie_id, rating):
        user_ratings = common.users.find_one({'id': user_id}, {'_id': 0})['ratings']
        movie_deviations = common.deviations.find_one({'movie_id': movie_id}, {'_id': 0, 'deviations': 1})['deviations']

        for movie in user_ratings:
            card = movie_deviations[movie]['cardinality']
            dev = movie_deviations[movie]['deviation']

            new_dev = ( (card * dev) + (data['rating'] - user_ratings[movie]['rating']) ) / float(card + 1)

            # update
            # for new_movie vs movie = new_dev
            # for movie vs new_movie = -new_dev

            key = 'deviations.' + str(movie)
            common.deviations.update({'movie_id': data['movie_id']}, {'$set': {key : {'deviation': new_dev, 'cardinality': card + 1}}})

            key = 'deviations.' + str(data['movie_id'])
            common.deviations.update({'movie_id': int(movie)}, {'$set': {key : {'deviation': -new_dev, 'cardinality': card + 1}}})

    # Called using vectors obtained from self.get_movie_vectors
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
        user_count = common.users.count()
        print "Preparing movie vectors ( user count: %d )" % (user_count)
        movies = {}

        my_prbar = pyprind.ProgBar(user_count)

        for user in common.users.find():
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

        return deviation_matrix

    def get_deviation_matrix(self):
        return self.calculate_deviation_matrix()