import sys
import csv
import json
import tmdbsimple as tmdb
import pyprind
import collections

tmdb.API_KEY = 'd918f6e1124aa29073c2b6530bc35315'

def call_tmdb(id):
	global tmdb
	movie = tmdb.Movies(id)
	
	return movie.info()

def match_tmdb(path):

	matches = []
	movies = []

	tmdb_data = open( path + '/u.movies.tmdb', 'r' )

	tmdb_reader = csv.reader( tmdb_data , delimiter = "|")

	for line in tmdb_reader:
		matches.append(line[0])

	tmdb_data.close()
	matches[49] = 3
	
	my_prbar = pyprind.ProgBar(len(matches), width = 70)
	
	for mv_id, tmdb_id in enumerate(matches):
		
		movie = {
			'id': int(mv_id + 1),
			'tmdb_id': int(tmdb_id)
		}
		
		success = False
		
		while not success:
			
			try:
				info = call_tmdb(int(tmdb_id))
				success = True
			except:
				print 'Error Occured for movie_id: ' + str(mv_id + 1) + ', tmdb_id: ' + str(tmdb_id)
		
		info.pop('id', None)
		
		movie.update(info)
		movies.append(movie)
		
		my_prbar.update(item_id = int(mv_id))
		
	return movies

with open('items.json', 'w') as outfile:
    json.dump(match_tmdb('ml-100k'), outfile)
	
# sudo mongoimport --db hypertarget_ads --collection movies --type json --file items.json --jsonArray