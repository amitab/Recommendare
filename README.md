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

Example:

Lets consider a user:
```
{
    u'age': 24,
    u'sex': u'M',
    u'likes': [
        u'Mystery', u'Romance', u'Family', u'Science Fiction', u'Horror', u'Crime',
        u'Drama', u'Fantasy', u'Animation', u'Music', u'Adventure', u'Action', u'Comedy',
        u'Documentary', u'War', u'Thriller', u'History'],
    u'occupation': u'technician',
    u'id': 1,
    u'zip_code': u'85711'
}
```

We would build this user vector:
```
[
    0.25757575757575757,                    # The age normalized to a value between 0 and 1

    1, 0,                                   # Male or female

    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 1, 0,                 # So many occupations to choose from

    1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1,
    0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1,
    0, 0, 0, 0, 0, 0, 1, 1, 0               # He likes so many genres of Movies
]
```

We would construct another vector for the user we are trying to compare to and find the cosine of the angle between the two n-dimentional vector.
There are lots of 0's in our vectors, so Cosine Similarity seems like the best measure to use.

![equation](https://latex.codecogs.com/svg.latex?\cos&space;\left&space;(&space;x,&space;y&space;\right&space;)&space;=&space;\frac{x&space;.&space;y}{\sqrt{\sum_{i=1}^{n}x_{i}^{2}}&space;\times&space;\sqrt{\sum_{i=1}^{n}y_{i}^{2}}})

Numerator is just a dot product of the two vectors. Denominator is the product of the individual lengths of the vectors.
These values are caluculated before time, updated each time a user updates his interests and are used to fetch the k nearest neighbours.

![KNN](https://i.imgur.com/7XPJKZ1.png)

Once we have these neighbours, we find the common movies between these users and remove the movies already rated by the target user.

Finally, SlopeOne is used to find predicted rating of these movies for the target user with the following formula:

![slopeone](https://latex.codecogs.com/svg.latex?\frac{\sum_{u=0}^{n}(R_{u,i}&space;-&space;\overline{R_{u}})(R_{u,j}&space;-&space;\overline{R_{u}})}{\sqrt{\sum_{u=0}^{n}(R_{u,i}&space;-&space;\overline{R_{u}})^{2}}\sqrt{\sum_{u=0}^{n}(R_{u,j}&space;-&space;\overline{R_{u}})^{2}}})

# How to use

The main file is `hypertarget.py`. The usage is as described below.

```
h = Hypertarget()
h.hypertarget(1  # user_id,
              10 # number of movies to recommend,
              3  # number of neighbours to look for)
```

To register a user:
```
h = Hypertarget()
# All are required, except 'likes'
h.register_user({
    'zip_code': 3848920,
    'age': 99,
    'gender': 'F',
    'likes': ['Drama'], # Optional
    'occupation': 'Student'
})
```

To update a users likes:
```
h = Hypertarget()
h.update_user_likes(
    1         # user id
    ['Drama'] # new likes
)
```

To rate a Movie:
```
h = Hypertarget()
h.user_rate_movie(
    1,  # user id
    2,  # movie id
    4.2 # rating
)
```