# -*- coding: utf-8 -*-
"""Consumer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jdaYQdbYLdkNMHBHBOkiB9uyuSP8JMuH
"""

import pandas as pd
import numpy as np

import os
import requests
import zipfile
import io
import streamlit as st

from sklearn.preprocessing import LabelEncoder
import tensorflow.keras.models

from modelstore import ModelStore
import json

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
print(movie_dataset.head())

combined_dataset = pd.merge(u_data_dataset, movie_dataset, how='inner', on='movie id')

master_dataset = combined_dataset.groupby(by=['user id','movie title'], as_index=False).agg({"rating":"mean"})

user_encoder = LabelEncoder()
master_dataset['user'] = user_encoder.fit_transform(master_dataset['user id'].values)
n_users = master_dataset['user'].nunique()

movie_encoder = LabelEncoder()
master_dataset['movie'] = movie_encoder.fit_transform(master_dataset['movie title'].values)
n_movies = master_dataset['movie'].nunique()

master_dataset['rating'] = master_dataset['rating'].values.astype(np.float32)
min_rating = min(master_dataset['rating'])
max_rating = max(master_dataset['rating'])

print (master_dataset.head())

print("Dataset Loaded Successfully")

model_store = ModelStore.from_aws_s3("iiscmlops")
domain_name = "prod-movie-model"

model_path = model_store.download(
   local_path=".",
   domain=domain_name
)

model_name  = os.path.join(model_path, "model")
print ("Model path directory")
print (os.listdir(model_name))

model =  tensorflow.keras.models.load_model(model_name)
print(model)

def recommender_system(user_id, model, n_movies):

  print ("User ID ", user_id)  
  encoded_user_id = user_encoder.transform([user_id])

  seen_movies = list(master_dataset[master_dataset['user id'] == user_id]['movie'])
  unseen_movies = [i for i in range(min(master_dataset['movie']), max(master_dataset['movie'])+1) if i not in seen_movies]
  
  model_input = [np.asarray(list(encoded_user_id)*len(unseen_movies)), np.asarray(unseen_movies)]
  predicted_ratings = model.predict(model_input)
  
  predicted_ratings = np.max(predicted_ratings, axis=1)
  sorted_index = np.argsort(predicted_ratings)[::-1]
  recommended_movies = movie_encoder.inverse_transform(sorted_index)
  
#   print("Top", n_movies, "Movie recommendations for the User ", user_id, "are: ")
#   print(list(recommended_movies[:n_movies]))
  return list(recommended_movies[:n_movies])
    


# user_id= 5 # int(input("Enter user id: "))
# n_movies = 10 # int(input("Enter number of movies to be recommended: "))

st.title('IISc Project - Movie Recommendation System with MLOps')

user_id = st.text_input('Enter User ID', '20127')
st.write('User ID is', user_id)

n_movies = st.slider('Number of Movie Recommendation?', 0, 100, 5)
st.write("Recommending ", n_movies, 'movies with Deep Learning for User ID ', user_id )

# Call Recommendation Function with userid and n_movies

u = int(user_id)
n = int(n_movies)
result = recommender_system(u, model, n)

print ("Movie List")
print  (result)

df = pd.DataFrame(result, columns=['Movie Name'])
df.index += 1
st.write(df)


