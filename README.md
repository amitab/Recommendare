# Recommendare
A python based hybrid recommendation system built from scratch

# Requirements

* Python 2.7.*
* MongoDB
* Python Modules:
    * pyprind
    * pymongo
    * tmdbsimple (optional)
* ml-100k dataset from `http://www.grouplens.org/datasets/movielens/`

## Set it up:

Make a copy of the `.config.example` into the root directory as `.config` and add all your database information and you TMDB API key, if you want to use it.

Run `python install.py -p <path to extracted ml-100k>`. To include TMDB information, you can pass the `--with-tmdb` option. *WARNING!* Loading TMDB information takes quite a bit of time.

This script:
1. Downloads `u.data.tmdb` from `https://gist.github.com/amitab/7869d7336b80dfc3c4e8` to match movie IDs with TMDB IDs, if `--with-tmdb` option is provided.
2. Loads metadata, user data, movies data into MongoDB in the database and respective collections provided in the `.config` file.
3. Prepares Movie deviation matrix and imports into the collection provided in the `.config` file.
3. Prepares User Similarity matrix and imports into the collection provided in the `.config` file.

# Peek Inside

There are two components:
* The User Collaborative filter
* The Item Collaborative filter

The user similarity and item deviations are computed ahead of time and updated on User registration, User likes, and upon adding a new Movie. To recommend a movie to a user, the high level steps are: 
1. Use Cosine Similarity to get the k nearest neighbours
2. Find common movies between these neighbours excluding the movies the User has already rated
3. Predict the user rating of these movies using SlopeOne algorithm and the similarity of the users
4. Return a sorted list of movies.

To calculate cosine similarity between two Users, we develop a vector to represent the user.
This vector contains the normalized age, gender, occupation and genre interests. This is generated in `user_wrapper.py:40`.

# How to use

The main file is `hypertarget.py`. The usage is as described below.

```
from hypertarget import HyperTarget

h = HyperTarget()
h.hypertarget(<User Id>, <number of movies to recommend>, <number of neighbours to check. Default is 3>)
```