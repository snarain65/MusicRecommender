# -*- coding: utf-8 -*-
"""DTSC710_Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1o9eTPOKhT_Z90AEuBtENUxJpM-DVYHV2

#Project - Music Recommendation System
Selina Narain 1261565

Neelam Boywah 1226855

Zoya Haq 1222440

DTSC 710 - M01

Professor Liangwen Wu

Please open in Google Colab as Github does not render plotly visualizations.
"""

#import the necessary libraries
import os
import pandas as pd 
import numpy as np 
import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go
from sklearn.manifold import TSNE
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import euclidean_distances
from scipy.spatial.distance import cdist
import difflib
import warnings
warnings.filterwarnings("ignore")

#Mount the google drive to allow access to music recommendation data
from google.colab import drive 
drive.mount('/content/gdrive')

data = pd.read_csv("/content/gdrive/My Drive/DTSC710_Project/MRDatasets/data.csv")
genre_data = pd.read_csv('/content/gdrive/My Drive/DTSC710_Project/MRDatasets/data_by_genres.csv')
year_data = pd.read_csv('/content/gdrive/My Drive/DTSC710_Project/MRDatasets/data_by_year.csv')
artist_data = pd.read_csv('/content/gdrive/My Drive/DTSC710_Project/MRDatasets/data_by_artist.csv')

data.head()

genre_data.head()

year_data.head()

artist_data.head()

"""Visualizing year_data"""

#Generalizing year data to decades -- easier to visualize than having overwhelming data per year
def year_to_decade_conversion(year):
    decade_start = int(year/10) * 10
    decade = '{}s'.format(decade_start)
    return decade

data['decade'] = data['year'].apply(year_to_decade_conversion)

#Frequency of music over decades
decade_plot = sns.countplot(x=data["decade"], color="lightskyblue").set(title="Music Consumption Over the Decades")

#Intializing sound features and visualizing over the years
sound_features = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'valence', 'speechiness']

#Plot line graph 
sound_fig = px.line(year_data, x='year', y=sound_features, title='Sound Features over the Years')
sound_fig.show()

#Intializing top 20 genres based on popularity feature
top_genres = genre_data.nlargest(20, 'popularity')

#Feature values to be plotted per genre
genre_features = ['valence', 'energy', 'danceability']

#Plot bar graph
fig = px.bar(top_genres, x='genres', y=genre_features, barmode='group')
fig.show()

#Intializing top 20 artists based on popularity feature
top_songs = artist_data.nlargest(20, 'popularity')

#Feature values to be plotted per artist
artist_features = ['valence', 'energy', 'danceability']

#Plot bar graph
fig = px.bar(top_songs, x='artists', y=artist_features, barmode='group')
fig.show()

"""K-Means Clustering for Genres"""

feature_names = ['acousticness', 'danceability', 'duration_ms', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 
                 'valence', 'popularity', 'key']
                 
X = genre_data[feature_names]

# Create pipeline
genrecluster_pipeline = Pipeline([('scaler', StandardScaler()), ('kmeans', KMeans())])

# Define parameter grid
param_grid = {'kmeans__n_clusters': range(1, 20)}

# Create grid search object
grid_search = GridSearchCV(genrecluster_pipeline, param_grid, cv=5)

# Fit grid search
grid_search.fit(X)

# Print best parameters
print("Best parameters:", grid_search.best_params_)

# Perform clustering on genre data

#Pipeline - scaling data, performing k means clustering
genrecluster_pipeline = Pipeline([('scaler', StandardScaler()), ('kmeans', KMeans(n_clusters=19))])

#X -> Features: acousticness, danceability, duration_ms, energy, instrumentalness, liveness, loudness, speechiness, tempo, valence, popularity, key

#Fit clustering model
genrecluster_pipeline.fit(X)

#Predict model -> new column 'clusters'
genre_data['clusters'] = genrecluster_pipeline.predict(X)

#T-distributed Stochastic Neighbor Embedding (TSNE)
#TSNE is a tool to visualize high-dimensional data

#tsne_genre_pipeline variable creates a pipeline object that scales the data using StandardScaler() 
#Also applies t-SNE algorithm with 2 output dimensions and verbose mode on.
tsne_genre_pipeline = Pipeline([('scaler', StandardScaler()), ('kmeans', KMeans(n_clusters=19)), ('tsne', TSNE(n_components=2, verbose=1))])

#Transform X into a 2-dimensional embedded space
genre_transformed = tsne_genre_pipeline.fit_transform(X)

#Creates a Pandas DataFrame called 'genre_df_proj' with columns 'x', 'y', 'genres', and 'clusters',
genre_df_proj = pd.DataFrame(columns=['x', 'y'], data=genre_transformed)
genre_df_proj['genres'] = genre_data['genres']
genre_df_proj['clusters'] = genre_data['clusters']

#Plot clusters
fig = px.scatter(genre_df_proj, x='x', y='y', color='clusters', hover_data=['x', 'y', 'genres'], color_continuous_scale = "viridis")
fig.update_layout(title='TSNE visualization of music genres clustered by audio features', xaxis_title='X', yaxis_title='Y')
fig.show()
import plotly.io as pio

# Get cluster centroids
centroids = tsne_genre_pipeline.named_steps['tsne'].embedding_
centroids = pd.DataFrame(centroids, columns=['x', 'y'])
centroids = centroids.groupby(genre_data['clusters']).mean()
centroids.index.name = 'clusters'

fig.update(data=[])

# Add centroids to the scatter plot
fig.add_trace(go.Scatter(x=centroids['x'], y=centroids['y'], mode='markers', marker=dict(symbol='star', size=15)))
fig.show()

"""K-Means Clustering for Songs"""

feature_names = ['valence', 'year', 'acousticness', 'danceability', 'duration_ms', 'energy', 'instrumentalness', 'liveness',	
                 'loudness',	'mode', 'popularity', 'speechiness', 'tempo']
                 
X = data[feature_names]

# Create pipeline
songs_cluster_pipeline = Pipeline([('scaler', StandardScaler()), ('kmeans', KMeans())])

# Define parameter grid
param_grid = {'kmeans__n_clusters': range(1, 25)}

# Create grid search object
grid_search = GridSearchCV(songs_cluster_pipeline, param_grid, cv=5)

# Fit grid search
grid_search.fit(X)

# Print best parameters
print("Best parameters:", grid_search.best_params_)

# Perform clustering on songs data

#Pipeline - scaling data, performing k means clustering
song_cluster_pipeline = Pipeline([('scaler', StandardScaler()), ('kmeans', KMeans(n_clusters=24, verbose=False))], verbose=False)

#X Features: valence, year, acousticness, danceability, duration_ms, energy, instrumentalness, liveness, loudness,	mode, popularity, speechiness, tempo

#Fit clustering model
song_cluster_pipeline.fit(X)

#Predict model -> new column 'clusters'
song_cluster_labels = song_cluster_pipeline.predict(X)

#Adding cluster_label column to data
data['cluster_label'] = song_cluster_labels

#Pipeline - scaling data, performing PCA
pca_pipeline = Pipeline([('scaler', StandardScaler()), ('PCA', PCA(n_components=2))])

#Transform X into a 2-dimensional embedded space
song_transformed = pca_pipeline.fit_transform(X)

#Creates a Pandas DataFrame called 'songs_df_proj' with columns 'x', 'y', 'title', and 'clusters',
songs_df_proj = pd.DataFrame(columns=['x', 'y'], data=song_transformed)
songs_df_proj['title'] = data['name']
songs_df_proj['cluster'] = data['cluster_label']

# Create the plot using Plotly Express
fig = px.scatter(songs_df_proj, x='x', y='y', color='cluster', hover_data=['title'], color_continuous_scale='viridis', labels={'x': 'PCA Component 1', 'y': 'PCA Component 2'}, title='Spotify Song Clusters')
fig.update_layout(legend_title='Cluster')
fig.show()

"""Recommendation System"""

!pip install spotipy

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from collections import defaultdict

# Initialize Spotify API client credentials
client_credentials_manager = SpotifyClientCredentials(client_id = "06a02c7776f3499db28b091835e3c254", client_secret = "f8c7d2dc515e470f84532896e2d47261")
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

# Function to find song details given its name and release year
def get_song(name, year):
    song_details_data = defaultdict() # Create an empty defaultdict to store song details

    # Search for the song on Spotify using track name and release year
    song_results = sp.search(q= 'track: {} year: {}'.format(name,year), limit=1)
    
    # Check if the search returned any results
    if song_results['tracks']['items'] == []:
        return None

    # Get details of the first search result (which is assumed to be the song we're looking for)
    song_results = song_results['tracks']['items'][0]
    trackID = song_results['id']
    audio_features = sp.audio_features(trackID)[0]

    # Extract relevant song details and store them in the defaultdict
    song_details_data['name'] = [name]
    song_details_data['year'] = [year]
    song_details_data['explicit'] = [int(song_results['explicit'])]
    song_details_data['duration_ms'] = [song_results['duration_ms']]
    song_details_data['popularity'] = [song_results['popularity']]

    for key, value in audio_features.items():
        song_details_data[key] = value
        
    # Convert the defaultdict to a Pandas DataFrame and return it
    return pd.DataFrame(song_details_data)

#Features to be used to recommend songs
features = ['valence', 'year', 'acousticness', 'danceability', 'duration_ms', 'energy',
            'instrumentalness', 'liveness', 'loudness', 'mode', 'popularity', 'speechiness', 'tempo']

def get_spotify_song_data(song, spotify_data):
    # Try to find the song in the dataframe based on name and year of release
    try:
      song_info_data = spotify_data[(spotify_data['name'] == song['name']) & (spotify_data['year'] == song['year'])].iloc[0]
      return song_info_data
    
    except IndexError:
      # If the song is not found in the dataframe, call the get_song function to get the song data from Spotify API
      return get_song(song['name'], song['year'])

def get_mean_val(song_list, spotify_data):
    # Initialize an empty list to hold the feature vectors for each song in the input list
    song_vecs = []
    
    # Iterate over each song in the input list
    for song in song_list:
      # Get the audio feature data for the song from the Spotify data DataFrame
      song_metadata = get_spotify_song_data(song, spotify_data)

      # If the song is not found in the Spotify data, print a warning and continue to the next song
      if song_metadata is None:
        print('Warning: {} does not exist in Spotify or in database'.format(song['name']))
        continue
      # Extract the audio feature values for the song as a numpy array and append it to the song_vecs list
      song_vec = song_metadata[features].values
      song_vecs.append(song_vec)
    
    # Convert the list of song feature vectors to a numpy array
    song_mtx = np.array(list(song_vecs))
    
    # Calculate the mean feature vector across all songs in the input list and return it
    return np.mean(song_mtx, axis=0)

def flatten_dict_list(dict_list):
  flattened_dict = defaultdict() # Create an empty defaultdict for flattened dictionary
  #Function iterates over each key-value pair in that dictionary
  for key in dict_list[0].keys():
    flattened_dict[key] = []
  
  #For each key-value pair, the value is appended to the corresponding list
  for dictionary in dict_list:
    for key, value in dictionary.items():
      flattened_dict[key].append(value)
      
  #Fully flattened dictionary is returned    
  return flattened_dict

def songs_recommendation(song_list, spotify_data, n_songs=5):
    #List of metadata columns we want to return for the recommended songs
    metadata_cols = ['name', 'year', 'artists', 'popularity']
    
    #Flattened version of the input song list where each song is represented as a dictionary
    song_dict = flatten_dict_list(song_list)
    
    #Mean vector of the input song list, calculated using get_mean_val()
    song_mean_vector = get_mean_val(song_list, spotify_data)

    #Scaler used in song_cluster_pipeline
    scaler = song_cluster_pipeline.steps[0][1]

    #Scaled data of all songs in the spotify_data DataFrame
    scaled_data = scaler.transform(spotify_data[features])
    scaled_song_mean_vector = scaler.transform(song_mean_vector.reshape(1, -1))

    #Matrix of cosine distances between scaled_song_mean_vector and scaled_data
    distances = cdist(scaled_song_mean_vector, scaled_data, 'cosine')

    #Top n_songs songs in spotify_data that are closest to song_mean_vector based on cosine distance
    index = list(np.argsort(distances)[:, :n_songs][0])
    
    #DataFrame of recommended songs based 
    song_recs = spotify_data.iloc[index]
    song_recs = song_recs[~song_recs['name'].isin(song_dict['name'])]
    
    #Returned dictionary with recommended song and its corresponding metadata
    return song_recs[metadata_cols].to_dict(orient='records')

songs_recommendation([{'name': 'Flowers', 'year':2023}], data)

