# -*- coding: utf-8 -*-
"""Consumer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jdaYQdbYLdkNMHBHBOkiB9uyuSP8JMuH
"""

import pandas as pd
import numpy as np

import requests
import zipfile
import io

from sklearn.preprocessing import LabelEncoder
import tensorflow.keras.models

DATASET_LINK='http://files.grouplens.org/datasets/movielens/ml-100k.zip'

r = requests.get(DATASET_LINK)
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall()

u_info = pd.read_csv('ml-100k/u.info', header=None)
print(u_info)

u_data_str = 'user id | movie id | rating | timestamp'
u_data_headers = u_data_str.split(' | ')

u_data_dataset = pd.read_csv('ml-100k/u.data', sep='\t',header=None,names=u_data_headers)
print(u_data_dataset.head())

len(u_data_dataset), max(u_data_dataset['movie id']),max(u_data_dataset['movie id'])

u_item_str = 'movie id | movie title | release date | video release date | IMDb URL | unknown | Action | Adventure | Animation | Children | Comedy | Crime | Documentary | Drama | Fantasy | Film-Noir | Horror | Musical | Mystery | Romance | Sci-Fi | Thriller | War | Western'
u_item_headers = u_item_str.split(' | ')
print(u_item_headers)

items_dataset = pd.read_csv('ml-100k/u.item', sep='|',header=None,names=u_item_headers,encoding='latin-1')
movie_dataset = items_dataset[['movie id','movie title']]
movie_dataset.head()

combined_dataset = pd.merge(u_data_dataset, movie_dataset, how='inner', on='movie id')

master_dataset = combined_dataset.groupby(by=['user id','movie title'], as_index=False).agg({"rating":"mean"})
master_dataset

user_encoder = LabelEncoder()
master_dataset['user'] = user_encoder.fit_transform(master_dataset['user id'].values)
n_users = master_dataset['user'].nunique()

movie_encoder = LabelEncoder()
master_dataset['movie'] = movie_encoder.fit_transform(master_dataset['movie title'].values)
n_movies = master_dataset['movie'].nunique()

master_dataset['rating'] = master_dataset['rating'].values.astype(np.float32)
min_rating = min(master_dataset['rating'])
max_rating = max(master_dataset['rating'])
n_users, n_movies, min_rating, max_rating

print (master_dataset.head())

print("Database Loaded")

model_name = 'movie_model.h5'

model =  tensorflow.keras.models.load_model(model_name)

def recommender_system(user_id, model, n_movies):

  encoded_user_id = user_encoder.transform([user_id])

  seen_movies = list(master_dataset[master_dataset['user id'] == user_id]['movie'])
  unseen_movies = [i for i in range(min(master_dataset['movie']), max(master_dataset['movie'])+1) if i not in seen_movies]
  
  model_input = [np.asarray(list(encoded_user_id)*len(unseen_movies)), np.asarray(unseen_movies)]
  predicted_ratings = model.predict(model_input)
  
  predicted_ratings = np.max(predicted_ratings, axis=1)
  sorted_index = np.argsort(predicted_ratings)[::-1]
  recommended_movies = movie_encoder.inverse_transform(sorted_index)
  
  
  print("Top", n_movies, "Movie recommendations for the User ", user_id, "are: ")
  print(list(recommended_movies[:n_movies]))

print(model)

user_id= int(input("Enter user id: "))
n_movies = int(input("Enter number of movies to be recommended: "))
recommender_system(user_id,model,n_movies)