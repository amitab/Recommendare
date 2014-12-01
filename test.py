import datetime

from hypertarget import Hypertarget

ht = Hypertarget()
a = datetime.datetime.now()
print ht.recommender.recommend(479, 100)
b = datetime.datetime.now()

c = b - a
print "Time Taken: " + str(c.microseconds)

