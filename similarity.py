import math

def pearsons_similarity(vector_x, vector_y):
    vx_sum = sum(vector_x) or 0
    vy_sum = sum(vector_y) or 0
    vx_sq_sum = sum([x ** 2 for x in vector_x]) or 0
    vy_sq_sum = sum([x ** 2 for x in vector_y]) or 0
    vx_x_vy = sum([x * y for x, y in zip(vector_x, vector_y)]) or 0

    similarity = vx_x_vy - (vx_sum * vy_sum) / float(len(vector_x))
    den = math.sqrt(vx_sq_sum - (vx_sum ** 2)/float(len(vector_x))) * math.sqrt(vy_sq_sum - (vy_sum ** 2)/float(len(vector_x)))

    if den == 0:
        return 0
    else:
        return similarity / float(den)

def sine_similarity(cosine_similarity):
    return math.sqrt(1 - cosine_similarity ** 2)

def cosine_similarity(vector_x, vector_y):
    dot_pdt = sum([x * y for x, y in zip(vector_x, vector_y)]) or 0
    length_x = math.sqrt(sum([x ** 2 for x in vector_x])) or 0
    length_y = math.sqrt(sum([x ** 2 for x in vector_y])) or 0

    den = length_x * length_y

    if den == 0:
        return 0
    else:
        return dot_pdt / float(den)

# deviations = {
#   'PSY': {
#     'Taylor Swift': {
#         'deviation': -2.0, 'cardinality': 2
#     },
#     'Whitney Houston': {
#         'deviation': -0.75, 'cardinality': 2
#     }
#   },
#   'Taylor Swift ': {
#     'PSY': {
#         'deviation': 2.0 , 'cardinality': 2
#     },
#     'Whitney Houston': {
#         'deviation': 1.0, 'cardinality': 2
#     }
#   },
#   'Whitney Houston': {
#     'PSY': {
#         'deviation': 0.75, 'cardinality': 2
#     },
#     'Taylor Swift': {
#         'deviation': -1.0, 'cardinality': 2
#     }
#   }
# }

# users = {
#     "Amy": {
#       "Taylor Swift": 4,
#       "PSY": 3,
#       "Whitney Houston": 4
#     },
#     "Ben": {
#       "Taylor Swift": 5,
#       "PSY": 2
#     },
#     "Clara": {
#       "PSY": 3.5,
#       "Whitney Houston": 4
#     },
#     "Daisy": {
#       "Taylor Swift": 5,
#       "Whitney Houston": 3
#     }
#   }

# def predict_rating(user_id, movie_id):
#     user_ratings = users[user_id]
#     movie_deviations = deviations[movie_id]

#     num = 0
#     den = 0

#     for movie in user_ratings:
#         if movie != movie_id:
#             num += (movie_deviations[movie]['deviation'] + user_ratings[movie]) * movie_deviations[movie]['cardinality']
#             den += movie_deviations[movie]['cardinality']

#     if den == 0:
#         print user_id, movie_id, ' = ', 0
#         return 0
#     else:
#         print user_id, movie_id, ' = ', num / float(den)
#         import pdb; pdb.set_trace()
#         return num / float(den)