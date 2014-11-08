import sys
import csv
import json

users = {}
movies = {}
meta = {
    'genres': ['unknown', 'action', 'adventure', 'animation', 'children', 'comedy', 'crime', 'documentary', 'drama', 'fantasy', 'film-noir', 'horror', 'musical', 'mystery', 'romance', 'sci-fi', 'thriller', 'war', 'western']
}

genres = ['unknown', 'action', 'adventure', 'animation', 'children', 'comedy', 'crime', 'documentary', 'drama', 'fantasy', 'film-noir', 'horror', 'musical', 'mystery', 'romance', 'sci-fi', 'thriller', 'war', 'western']

def load_movie_db(path):
    
    #load movie data
    
    i_f = open( path + '/u.movies.csv', 'r' )
    reader = csv.reader( i_f , delimiter = '|')
    for line in reader:
        if not line[0] in movies.keys():
            movies[line[0]] = {
                'id': int(line[0]),
                'ratings': {}
            }
        movies[line[0]]['name'] = line[1]
        movies[line[0]]['release_date'] = line[2]
        movies[line[0]]['url'] = line[3]
        movies[line[0]]['genre'] = []
        for i in range(0, 19):
            if line[4 + i] == "1":
                movies[line[0]]['genre'].append(genres[i])
    i_f.close()
    
    # load user data
    
    i_f = open( path + '/u.user', 'r' )
    reader = csv.reader( i_f , delimiter = '|')
    meta['occupations'] = set()
    meta['zip_codes'] = set()
    for line in reader:
        if not line[0] in users.keys():
            users[line[0]] = {
                'id': int(line[0])
            }
        users[line[0]]['age'] = int(line[1])
        users[line[0]]['sex'] = line[2]
        users[line[0]]['occupation'] = line[3]
        meta['occupations'].add(line[3])
        users[line[0]]['zip_code'] = line[4]
        meta['zip_codes'].add(line[4])
        
    i_f.close()
    meta['occupations'] = list(meta['occupations'])
    meta['zip_codes'] = list(meta['zip_codes'])
    
    # load user ratings
    
    i_f = open( path + '/u.data', 'r' )
    reader = csv.reader( i_f , delimiter = "\t")
    for line in reader:
        if not line[1] in movies.keys():
            movies[line[1]] = {
                'id': int(line[1]),
                'ratings': {}
            }
        movies[line[1]]['ratings'][int(line[0])] = {
            'rating': int(line[2]),
            'timestamp': int(line[3])
        }
    i_f.close()

load_movie_db(sys.argv[1])

with open('users.json', 'w') as outfile:
    json.dump(users.values(), outfile)
    
with open('movies.json', 'w') as outfile:
    json.dump(movies.values(), outfile)

with open('meta.json', 'w') as outfile:
    json.dump(meta, outfile)

# sudo mongoimport --db hypertarget_ads --collection users --type json --file users.json --jsonArray
# sudo mongoimport --db hypertarget_ads --collection movies --type json --file movies.json --jsonArray
# sudo mongoimport --db hypertarget_ads --collection meta --type json --file meta.json --jsonArray
    