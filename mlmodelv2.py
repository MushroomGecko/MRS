import database
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction import DictVectorizer

def liked_movies(movies):
    # print(movies)
    for i in list(movies):
        i['Likes'] = 1
    # print(movies)
    return movies


def disliked_movies(movies):
    # print(movies)
    for i in movies:
        # print(i)
        i['Likes'] = 0
    # print(movies)
    return movies


def simplify(movies):
    ret_vector = []
    for i in movies:
        movie = {}
        # print(i)
        if 'Title' not in i or i['Title'] == []:
            movie['Title'] = ""
        else:
            movie['Title'] = i['Title'][0]
        if 'Description' not in i or i['Description'] == []:
            movie['Description'] = ""
        else:
            movie['Description'] = i['Description'][0]
        if 'Genre' not in i or i['Genre'] == []:
            movie['Genre'] = ""
        else:
            movie['Genre'] = i['Genre'][0]
        if 'Director' not in i or i['Director'] == []:
            movie['Director'] = ""
        else:
            movie['Director'] = i['Director'][0]
        if 'Rating' not in i or i['Rating'] == []:
            movie['Rating'] = ""
        else:
            movie['Rating'] = i['Rating'][0]
        if 'Original Language' not in i or i['Original Language'] == []:
            movie['Original Language'] = ""
        else:
            movie['Original Language'] = i['Original Language'][0]
        if 'Cast' not in i or i['Cast'] == []:
            movie['Cast'] = ""
        else:
            movie['Cast'] = i['Cast'][0]
        if 'Likes' in i:
            movie['Likes'] = i['Likes']
        ret_vector.append(movie)
        # print(movie)
    return ret_vector


def find_best(liked, disliked, combined):

    movie_data = liked_movies(liked) + disliked_movies(disliked)
    movie_data_simp = simplify(movie_data)
    # for i in movie_data:
    # print(i)
    # Create a DataFrame from the sample data
    df = pd.DataFrame(movie_data_simp)
    # print(df)

    # Combine all features
    X = df.drop("Likes", axis=1)
    # print(X)
    y = df['Likes']

    vec = DictVectorizer(sparse=False)
    X_encoded = vec.fit_transform(X.to_dict(orient='records'))

    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.1, shuffle=True)

    # Create a Logistic Regression model
    lr_model = LogisticRegression()

    # Fit the model on the training data
    lr_model.fit(X_train, y_train)

    removals, new_movies = database.slim_listv2(combined)

    new_movies = simplify(new_movies)

    highest_value = 0.0
    highest_movie = ""
    for i in new_movies:
        new_data = vec.transform(i)
        probabilities = lr_model.predict_proba(new_data)

        # Extract the probability for the malicious class (class 1)
        confidence = probabilities[:, 1][0]

        print(i['Title'], confidence)
        if confidence > highest_value and i not in removals:
            highest_value = confidence
            highest_movie = i

    print()
    title = highest_movie['Title']
    description = highest_movie['Description']
    ret_movie = database.get_all_type_title_desc_strict_db(title, description)
    print(ret_movie['Title'][0], highest_value)

    return ret_movie
