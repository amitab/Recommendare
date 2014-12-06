"""
import datetime

from hypertarget import Hypertarget
ht = Hypertarget()

a = datetime.datetime.now()
print ht.recommender.recommend(944, 100)
b = datetime.datetime.now()

c = b - a
print "Time Taken: " + str(c.microseconds)
"""

"""
from user_wrapper import UserWrapper

uw = UserWrapper()
data = {
    'rating': 1,
    'movie_id': 515,
    'user_id': 479
}

uw.rate_movie(data)
print ht.recommender.recommend(479, 100)
"""
for i, char in enumerate('1324AND'):
    print ord(char)
