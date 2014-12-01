from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.hypertarget_ads

f = open('pwdlist', 'r')
lines = f.readlines().strip()
f.close()

i = 0

for user in db.users.find():
    #db.users.update({'id': user['id']}, {'$set': {'pwd': lines[i]}})
    print lines[i]
    i = i + 1
