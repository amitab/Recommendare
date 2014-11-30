# Recommendare
A python based hybrid recommendation system built from scratch

## Set it up:

If you are using Debian or Ubuntu, just run setup.sh to install required components and setup the database.

Else:

* Download the movie lens dataset from http://www.grouplens.org/datasets/movielens/
* Extract it and pass the directory path + the extracted folder to the extracted directory to extractor.py in the data folder ( in bash type: python extractor.py ml-100k )
* Install MongoDB if you don't have it already
* Download the tmdb information of the movies into the ml-100k folder from here (thanks to gilbitron): https://gist.githubusercontent.com/amitab/7869d7336b80dfc3c4e8/raw/u.item.tmdb
* Run match_tmdb.py which is in the data folder
* Import user.json, meta.json and items.json using the following commands:
```shell
sudo mongoimport --db hypertarget_ads --collection users --type json --file users.json --jsonArray
sudo mongoimport --db hypertarget_ads --collection movies --type json --file items.json --jsonArray
sudo mongoimport --db hypertarget_ads --collection meta --type json --file meta.json --jsonArray
```
* Run precompute.py
* Import all the json files into MongoDB using the following commands:
```shell
sudo mongoimport --db hypertarget_ads --collection deviations --type json --file deviation.json --jsonArray
sudo mongoimport --db hypertarget_ads --collection user_similarity --type json --file user_similarity.json --jsonArray
```
    