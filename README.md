# Recommendare

A python based hybrid recommendation system built from scratch.

## Requirements

* Python 2.7.*
* MongoDB
* Python Modules:
  * pyprind
  * pymongo
  * tmdbsimple (optional)
* ml-100k dataset from `http://www.grouplens.org/datasets/movielens/`

### Set it up

Make a copy of the `.config.example` into the root directory as `.config` and add all your database information and you TMDB API key, if you want to use it.

Run `python install.py -p <path to extracted ml-100k>`. To include TMDB information, you can pass the `--with-tmdb` option. *WARNING!* Loading TMDB information takes quite a bit of time.

This script:

1. Downloads `u.data.tmdb` from `https://gist.github.com/amitab/7869d7336b80dfc3c4e8` to match movie IDs with TMDB IDs, if `--with-tmdb` option is provided.
2. Loads metadata, user data, movies data into MongoDB in the database and respective collections provided in the `.config` file.
3. Prepares Movie deviation matrix and imports into the collection provided in the `.config` file.
3. Prepares User Similarity matrix and imports into the collection provided in the `.config` file.

## Peek Inside

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

_Example_:

Lets consider a user with ID 1:

```json
{
    "age" : 24,
    "sex" : "M",
    "likes" : [
        "Mystery", "Romance", "Sci-Fi",
        "Family", "Horror", "Film-Noir",
        "Crime", "Drama", "Children's",
        "Musical", "Animation", "Adventure",
        "Action", "Comedy", "Documentary",
        "War", "Thriller", "Western"
    ],
    "occupation" : "technician",
    "id" : 1,
    "zip_code" : "85711"
}
```

We would build user vector for user ID 1 as:

```json
[
    # The age normalized to a value between 0 and 1
    0.25757575757575757,

    # Male or female
    1, 0,

    # So many occupations to choose from
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 1, 0,

    # He likes so many genres of Movies
    1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1,
    0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1,
    0, 0, 0, 0, 0, 0, 1, 1, 0
]
```

We would construct another vector for the user we are trying to compare to and find the cosine of the angle between the two n-dimentional vector.
There are lots of 0's in our vectors, so Cosine Similarity seems like the best measure to use.

![Cosine Similarity](https://latex.codecogs.com/svg.latex?\cos&space;\left&space;\(&space;x,&space;y&space;\right&space;\)&space;=&space;\frac{x&space;.&space;y}{\sqrt{\sum_{i=1}^{n}x_{i}^{2}}&space;\times&space;\sqrt{\sum_{i=1}^{n}y_{i}^{2}}})

Numerator is just a dot product of the two vectors. Denominator is the product of the individual lengths of the vectors.
These values are caluculated before time, updated each time a user updates his interests and are used to fetch the k nearest neighbours.

![KNN](https://i.imgur.com/7XPJKZ1.png)

Once we have these neighbours, we pick some of the movies between these users and remove the movies already rated by the target user.
Then we predict a rating for each of these movies for the target user based on the movies the user has already rated, using both the SlopeOne and the Cosine Similarity algorithm.

### Cosine Similarity rating predictor

It's simple. We already have the cosine similarity of the neighbours. The rating of a movie ![i](https://latex.codecogs.com/svg.latex?i) is given by:

![\frac{\sum_{k\epsilon N}u_{i}^{k} \cdot S\left ( u^{k},u^{r}\right )}{\sum_{k\epsilon N}S\left ( u^{k},u^{r}\right )}](https://latex.codecogs.com/gif.latex?\frac{\sum_{k\epsilon&space;N}u_{i}^{k}&space;\cdot&space;S\left&space;\(&space;u^{k},u^{r}\right&space;\)}{\sum_{k\epsilon&space;N}S\left&space;\(&space;u^{k},u^{r}\right&space;\)})

Where:
![N](https://latex.codecogs.com/svg.latex?N) is the set of all neighbours
![Target User](https://latex.codecogs.com/svg.latex?u^{r}) is the target user
![Neighbour User](https://latex.codecogs.com/svg.latex?u^{k}) is the neighbour user
![Neighbour User Rating](https://latex.codecogs.com/svg.latex?u_{i}^{k}) is the neighbour user rating

### SlopeOne rating predictor

**First Phase**: We calculate the deviation between every pair of movies - ![i](https://latex.codecogs.com/svg.latex?i) and ![j](https://latex.codecogs.com/svg.latex?j) and store them somewhere.

If ![X](https://latex.codecogs.com/svg.latex?X) is the entire set of ratings and ![S](https://latex.codecogs.com/svg.latex?S_{i,j}(X)) is the number of users who have rated both movies ![i](https://latex.codecogs.com/svg.latex?i) and ![j](https://latex.codecogs.com/svg.latex?j), then:

![card(Si,j(X))](https://latex.codecogs.com/svg.latex?dev_{i,j}&space;=&space;\sum_{u\epsilon&space;S_{i,j}\(X\)}\frac{u_{i}&space;-&space;u_{j}}{card\(S_{i,j}\(X\)\)})

**Second Phase**: To predict a rating for a movie ![j](https://latex.codecogs.com/svg.latex?j) by a user, we find the list of all the movies this user has rated : ![S(u) - {j}](https://latex.codecogs.com/gif.latex?S%28u%29%20-%20%5Cleft%20%5C%7B%20j%20%5Cright%20%5C%7D)

![SlopeOne](https://latex.codecogs.com/svg.latex?%5Cfrac%7B%5Csum_%7Bi%5Cepsilon%20S%5Cleft%20%28%20u%20%5Cright%20%29-%5Cleft%20%5C%7B%20j%20%5Cright%20%5C%7D%7D%5Cleft%20%28%20dev_%7Bi%2Cj%7D&plus;u_%7Bi%7D%20%5Cright%20%29c_%7Bi%2Cj%7D%7D%7B%5Csum_%7Bi%5Cepsilon%20S%5Cleft%20%28%20u%20%5Cright%20%29-%5Cleft%20%5C%7B%20j%20%5Cright%20%5C%7D%7Dc_%7Bi%2Cj%7D%7D)

where ![card](https://latex.codecogs.com/svg.latex?c_{i,j}) is the number of users who have rated both ![i](https://latex.codecogs.com/svg.latex?i) and ![j](https://latex.codecogs.com/svg.latex?j).

### Combining the two ratings - The Hybrid Rating Predictor

Just average of the two. Nothing special.

## How movies are picked for recommendation

There are 3 types of recommenders built in, all varying depending on the way the movies are selected for recommendation.

1. **The Fast Recommender** - Pick the `k` nearest neighbours, pick `count` of their highly rated movies and run it through the hybrid rating predictor.
2. **The Best Recommender** - Pick all the movies of `k` neighbours, run it through the hybrid rating predictor and pick `count` best rated movies.
3. **The Serendipity Recommender** - Always returns random best results. Pick the `k` nearest neighbours, pick `count` random movies from their highly rated list and run it through the hybrid rating predictor.

You can see the implementation of each of these in `Recommendare.py`.

## How to use

The main file is `Recommendare.py`. The usage is as described below.

```python
r = Recommendare()

# Function signature is the same for fast, best, serendipity recommenders
r.fast_recommender( 1  # user_id,
                   10  # number of movies to recommend,
                    3  # number of neighbours to look for)
```

To register a user:

```python
r = Recommendare()
# All are required, except 'likes'. It is built as the user rates movies.
r.register_user({
    'zip_code': 3848920,
    'age': 99,
    'gender': 'F',
    'likes': ['Drama'], # Optional
    'occupation': 'Student'
})
```

To update a users likes:

```python
r = Recommendare()
r.update_user_likes(
    1         # user id
    ['Drama'] # new likes
)
```

To rate a Movie:

```python
r = Recommendare()
r.user_rate_movie(
    1,  # user id
    2,  # movie id
    4.2 # rating
)
```

To predict a rating for a Movie by a User:

```python
r = Recommendare()
r.predict_rating(
    1,  # user id
    2,  # movie id
    3,  # neighbours to consult
)
```