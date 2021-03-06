import pyprind

import common

class SlopeOne(object):
    # Just with item IDs
    def calculate_devation(self, item1, item2):
        data = list(common.users.aggregate([
            {'$match': {'$and': [
                {'ratings.movie_id': item1},
                {'ratings.movie_id': item2}
            ]}},
            {'$unwind': '$ratings'},
            {'$match': {'ratings.movie_id': {'$in': [item1, item2]}}},
            {'$group': {
                '_id': '$ratings.movie_id',
                'sum': {'$sum': '$ratings.rating'},
                'count': {'$sum': 1}
            }},
            {'$project': {
                '_id': 1,
                'nume': {'$divide': ['$sum', '$count']},
                'card': '$count'
            }}
        ]))

        if len(data) == 0:
            return { 'deviation': 0, 'cardinality': 0 }
        return { 'deviation': data[0]['nume'] - data[1]['nume'], 'cardinality': data[0]['card'] }

    def predict_ratings(self, user_id, movies):
        user_ratings = common.users.find_one({'id': user_id}, {'_id': 0, 'ratings': 1})['ratings']
        deviations = common.deviations.find({'movie_id': {'$in': [m['movie_id'] for m in movies]}}, {'_id': 0})

        return [{
            'movie_id': d['movie_id'],
            'rating': self._predict_rating(user_id, d['movie_id'], d['deviations'], user_ratings)
        } for d in deviations]

    def predict_rating(self, user_id, movie_id):
        user_ratings = common.users.find_one({'id': user_id}, {'_id': 0, 'ratings': 1})['ratings']
        movie_deviations = common.deviations.find_one({'movie_id': movie_id}, {'_id': 0, 'deviations': 1})['deviations']

        return self._predict_rating(user_id, movie_id, movie_deviations, user_ratings)

    def _predict_rating(self, user_id, movie_id, movie_deviations, user_ratings):
        num = 0
        den = 0

        for r in user_ratings:
            key = str(r['movie_id'])
            if r['movie_id'] != movie_id:
                num += (movie_deviations[key]['deviation'] + r['rating']) * movie_deviations[key]['cardinality']
                den += movie_deviations[key]['cardinality']

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
            for rating in user['ratings']:
                key = str(rating['movie_id'])
                if not key in movies:
                    movies[key] = {}
                movies[key][user['id']] = rating['rating']
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