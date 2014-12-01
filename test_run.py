from hypertarget import Hypertarget

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.hypertarget_ads

ht = Hypertarget()
data = ht.hypertarget(479)

user_seen = open('user_seen.data', 'w')
user_rec = open('user_rec.data', 'w')

for i, movie in enumerate(data):
    user_rec.write(str(i + 1) + ". " + str(movie['details']['title']) + "\n")
    genre_list = []
    
    for genre in movie['details']['genres']:
        genre_list.append(genre['name'])
        
    genre_list = ', '.join(genre_list)
    user_rec.write(genre_list + "\n")
    user_rec.write(str(movie['details']['vote_average']) + "\n")
    user_rec.write(str(movie['predicted_rating']) + "\n")

user_data = db.users.find_one({'id': 479}, {'_id': 0})
for i, rating in enumerate(user_data['ratings']):
    movie_name = db.movies.find_one({'id': int(rating)}, {'title': 1, '_id': 0})
    try:
        user_seen.write(unicode(str(i + 1), 'ascii') + ". " + unicode(str(movie_name['title']), 'ascii') + ": " + unicode(str(user_data['ratings'][rating]['rating']), 'ascii') + "\n")
    except:
        movie_name['title'] = movie_name['title'].encode('utf-8')
        user_seen.write(str(i + 1) + ". " + movie_name['title'] + ": " + str(user_data['ratings'][rating]['rating']) + "\n")
        
user_seen.close()
user_rec.close()
