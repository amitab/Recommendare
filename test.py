"""
from hypertarget import Hypertarget

ht = Hypertarget()
print ht.hypertarget(479)
"""

from Recommendare import Recommendare
import datetime

recommender = Recommendare()
a = datetime.datetime.now()
print recommender.recommend(479)
b = datetime.datetime.now()

c = b - a
print "Time Taken: " + str(c.microseconds)