from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.hypertarget_ads
genres_list = ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Disaster', 'Documentary', 'Drama', 'Eastern', 'Erotic', 'Family', 'Fan Film', 'Fantasy', 'Film Noir', 'Foreign', 'History', 'Holiday', 'Horror', 'Indie', 'Music', 'Musical', 'Mystery', 'Neo-noir', 'Road Movie', 'Romance', 'Science Fiction', 'Short', 'Sport', 'Sporting Event', 'Sports Film', 'Suspense', 'TV movie', 'Thriller', 'War', 'Western']


for user in db.users.find():
    likes = []
    for rating in user['ratings']:
        if user['ratings'][rating]['rating'] == 5:
            movie = db.movies.find_one({'id': int(rating)}, {'_id': 0, 'genres': 1})
            
            try:
                for genre in movie['genres']:
                    likes.append(genre['name'])
            except:
                print rating, user['id']
    likes = set(likes)
    db.users.update({'id': user['id']}, {'$set': {'likes': list(likes)}})
    
