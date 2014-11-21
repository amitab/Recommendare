# Recommendare
A python based hybrid recommendation system built from scratch

## Set it up:

If you are using Debian or Ubuntu, just run setup.sh to install required components and setup the database.

Else:

1. Download the movie lens dataset from http://www.grouplens.org/datasets/movielens/
2. Extract it and pass the directory path + the extracted folder to the extracted directory to extractor.py in the data folder ( in bash type: python extractor.py ml-100k )
3. Install MongoDB if you don't have it already
4. Import user.json, meta.json and movies.json using the following commands:
    ```shell
    sudo mongoimport --db hypertarget_ads --collection users --type json --file users.json --jsonArray
    sudo mongoimport --db hypertarget_ads --collection movies --type json --file movies.json --jsonArray
    sudo mongoimport --db hypertarget_ads --collection meta --type json --file meta.json --jsonArray
    ```
5. Run precompute.py
6. Import all the json files into MongoDB using the following commands:
    ```shell
    sudo mongoimport --db hypertarget_ads --collection deviations --type json --file deviation.json --jsonArray
    sudo mongoimport --db hypertarget_ads --collection user_similarity --type json --file user_similarity.json --jsonArray
    ```
    