from user_wrapper import UserWrapper
from Recommendare import Recommendare
from slopeone import SlopeOne

from pymongo import MongoClient

uw = UserWrapper()
"""
data1 = {
    'age': 22,
    'sex': 'M',
    'occupation': 'student',
    'zip_code': '560070'
}

data2 = {
    'age': 21,
    'sex': 'M',
    'occupation': 'student',
    'zip_code': '560004'
}

data3 = {
    'age': 20,
    'sex': 'M',
    'occupation': 'student',
    'zip_code': '560016'
}

uw.register_user(data1)
uw.register_user(data2)
uw.register_user(data3)
"""

"""
rate1 = {
    'rating': 4,
    'movie_id': 515,
    'user_id': 944,
}

rate2 = {
    'rating': 4,
    'movie_id': 515,
    'user_id': 945,
}
rate3 = {
    'rating': 4,
    'movie_id': 515,
    'user_id': 946,
}

uw.rate_movie(rate1)
uw.rate_movie(rate2)
uw.rate_movie(rate3)
"""

client = MongoClient('localhost', 27017)
db = client.hypertarget_ads

so = SlopeOne(db)

print so.predict_rating(946, 500)
