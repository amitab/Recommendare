import os
import sys
import csv
import json
import pyprind
import urllib2

import common

from collections import defaultdict
from pymongo import MongoClient
from usersimilarity import UserSimilarity
from slopeone import SlopeOne
from shutil import copyfile

try:
    import tmdbsimple as tmdb
    TMDB_PRESENT = True
except:
    TMDB_PRESENT = False

tmdb.API_KEY = common.tmdb_key
errors = []

TMDB_CACHE_PATH = 'data/tmdb_cache.json'
TMDB_MATCH_PATH = 'data/u.data.tmdb'
TMDB_ERRORS_PATH = 'data/errors.json'

users = defaultdict(dict)
movies = defaultdict(dict)
meta = defaultdict(dict)
id_to_movie = {}
try:
    print "Loaded TMDB Cache"
    tmdb_cache = json.load(open(TMDB_CACHE_PATH, 'r'))
except:
    print "No TMDB Cache"
    tmdb_cache = {}

def load_meta(path):
    print "Loading Metadata"
    file = open(path + '/u.genre', 'r')
    reader = csv.reader( file , delimiter = '|')
    meta['genres'] = [x[0] for x in reader if x]
    file.close()

    file = open(path +'/u.occupation', 'r')
    meta['occupations'] = [x for x in file.readlines() if x]
    file.close()

    meta['occupations'] = set()
    meta['zip_codes'] = set()
    meta['genders'] = set()

#load movie data
def load_movie_db(path, with_tmdb=TMDB_PRESENT):
    i_f = open( path + '/u.item', 'r' )
    reader = csv.reader( i_f , delimiter = '|')
    for line in reader:
        for i, word in enumerate(line):
            try:
                line[i] = unicode(word, 'utf-8')
            except:
                line[i] = line[i].decode('latin-1')

        movies[line[1]] = {
            'id': int(line[0]),
            'name': line[1],
            'release_date': line[2],
            'url': line[4],
            'genres': [meta['genres'][i] for i in range(0, 19) if line[5 + i] == "1"]
        }
        id_to_movie[line[0]] = line[1]
    i_f.close()

    if not with_tmdb:
        return

    genres = [x['name'] for x in tmdb.Genres().movie_list()['genres']]
    meta['genres'] = list(set(genres + meta['genres']))

    tmdb_data = open( path + '/u.movies.tmdb', 'r' )
    tmdb_reader = csv.reader( tmdb_data , delimiter = "|")
    matches = [(line[1], line[0]) for line in tmdb_reader]
    tmdb_data.close()
    my_prbar = pyprind.ProgBar(len(matches), width = 70, title='Loading Tmdb info')

    errors = []
    print "Starting Movie Import from TmDB"
    for m_key, tmdb_id in matches:
        try:
            key = unicode(m_key, 'utf-8')
        except:
            key = m_key.decode('latin-1')
        movies[key]['tmdb_id'] = int(tmdb_id)
        try:
            if str(tmdb_id) in tmdb_cache:
                info = tmdb_cache[str(tmdb_id)]
            else:
                info = tmdb.Movies(int(tmdb_id)).info()
                tmdb_cache[str(tmdb_id)] = info
        except Exception as e:
            print e
            print 'Error Occured to fetch movie_id: ' + key + ', tmdb_id: ' + str(tmdb_id)
            errors.append((key, tmdb_id))
            if '404' not in e.message:
                raise e
            continue

        info.pop('id', None)
        movies[key]['genres'].extend([
            x['name'] for x in info.pop('genres', [])
        ])
        movies[key]['genres'] = list(set(movies[key]['genres']))
        movies[key].update(info)
        my_prbar.update(item_id = int(movies[key]['id']), force_flush=True)

    with open(TMDB_ERRORS_PATH, 'w') as outfile:
        json.dump(errors, outfile, indent=4, sort_keys=True)

# load user data
def load_user_db(path):    
    i_f = open( path + '/u.user', 'r' )
    reader = csv.reader( i_f , delimiter = '|')
    for line in reader:
        users[line[0]] = {
            'id': int(line[0]),
            'age': int(line[1]),
            'sex': line[2],
            'occupation': line[3],
            'zip_code': line[4],
            'ratings': {},
            'likes': []
        }
        meta['genders'].add(line[2])
        meta['occupations'].add(line[3])
        meta['zip_codes'].add(line[4])
    i_f.close()
    
# load user ratings
def load_ratings(path):
    i_f = open( path + '/u.data', 'r' )
    reader = csv.reader( i_f , delimiter = "\t")
    for line in reader:
        users[line[0]]['ratings'][line[1]] = {
            'rating': int(line[2]),
            'timestamp': int(line[3])
        }
        if line[2] == '5':
            genres = movies[id_to_movie[line[1]]]['genres']
            try:
                genres.remove('unknown')
            except:
                pass
            users[line[0]]['likes'] = list(set(users[line[0]]['likes'] + genres))
    i_f.close()

def finalize():
    meta['occupations'] = list(meta['occupations'])
    meta['zip_codes'] = list(meta['zip_codes'])
    meta['genders'] = list(meta['genders'])

    slope = SlopeOne()
    similarity = UserSimilarity()

    dev = slope.get_deviation_matrix()
    sim = similarity.get_similarity_matrix()

    print "Dropping database {}".format(common.database.name)
    common.client.drop_database(common.database.name)

    print "Importing Users into {}".format(common.users.name)
    common.users.insert_many(users.values())

    print "Importing Movies into {}".format(common.movies.name)
    common.movies.insert_many(movies.values())

    print "Importing Metadata into {}".format(common.meta.name)
    common.meta.insert_many([meta])

    print "Importing Deviation Matrix into {}".format(common.deviations.name)
    common.deviations.insert_many(dev.values())

    print "Importing User Similarity Matrix into {}".format(common.user_similarity.name)
    common.user_similarity.insert_many(sim.values())

def prepare_parser():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--data-path', type=str, required=True)
    parser.add_argument('-t', '--with-tmdb', action='store_true', default=False)
    return parser

if __name__ == '__main__':
    parser = prepare_parser()
    args = parser.parse_args()

    if args.with_tmdb:
        if not TMDB_PRESENT:
            print "Option --with-tmdb provided, but module tmdbsimple is not present."
            sys.exit(1)
        if not os.path.exists('data'):
            os.makedirs('data')
        if not os.path.isfile(TMDB_MATCH_PATH):
            import pdb; pdb.set_trace()
            print "Loading TMDB match info"
            filedata = urllib2.urlopen('https://gist.github.com/amitab/7869d7336b80dfc3c4e8')
            with open(TMDB_MATCH_PATH, 'wb') as f:
                f.write(filedata.read())

    try:
        load_meta(args.data_path)
        load_movie_db(args.data_path, args.with_tmdb)
        load_user_db(args.data_path)
        load_ratings(args.data_path)
        finalize()
    except Exception as e:
        print "Exception: ", e
        if args.with_tmdb:
            with open(TMDB_CACHE_PATH, 'w') as outfile:
                json.dump(tmdb_cache, outfile, indent=4, sort_keys=True)
            print "Saved TMDB cache in {}".format(TMDB_CACHE_PATH)