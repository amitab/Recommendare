import datetime

from hypertarget import Hypertarget

ht = Hypertarget()
a = datetime.datetime.now()
print ht.hypertarget(479, 10)
b = datetime.datetime.now()

c = b - a
print "Time Taken: " + str(c.microseconds)
    
