import os

from flask import Flask, session, redirect, request, url_for

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

# a session in the context of web applications:
# a container that allows us to store data inside
# allows us to be able to access this data as the user is moving from page to page in our web application
# we want to be able to access this data no matter what the user is visiting
# the session allows us to have a place to store this data

# in the context of the spotipy library:
# it needs a place where it can store the access token that it will use to interact with the spotify web API
# we are going to specify that where it can store that access token is inside the flask session that we are going to create

app = Flask(__name__)

# a session is a place for our web server (flask) to be able to access the data inside
# we do not want users tampering with the data inside that session
# to do that, we need to give flask a secret key that it can use to encrypt that data
app.config['SECRET_KEY'] = os.urandom(64)  # generate a string of 64 random bytes 
                                            # and assign it to the secret key config var

client_id = ' '
client_secret = ' '
redirect_uri = 'http://localhost:5000/callback'
scope = 'playlist-read-private'
# if we use multiple, this is how it would look:
# scope = 'playlist-read-private,streaming(,etc.)'

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True # set for debugging purposes - otherwise not necessary
)

# call this client sp and create an instance of Spotify
sp = Spotify(auth_manager=sp_oauth)

# writing our first endpoint
# when someone accesses the route of our web application, we want to do one of two things:
# 1. log in with their account
# 2. if they are already logged in - redirect them to an endpoint, 
# which will get all of their playlists and print them out on that page

@app.route('/')
def home():
    # check if they are already logged in
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for('get_playlists'))

@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code']) # this allows a user not having to continuesly login to spotify
    return redirect(url_for('get_playlists'))

@app.route('/get_playlists')
def get_playlists():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp.oauth.get_authorize_url()
        return redirect(auth_url)
    
    playlists = sp.current_user_playlists()
    
    # iterating through every playlist in this playlists results that we got back in the items key
    # itemsis esentially the list of all the user's playlists
    # we extract the name as well as the spotify url for that particular playlist
    # we sort this playlist info, and then create an html response
    # br stands for line break
    # prints out the name of the playlist, along with the url on its own line
    playlists_info = [(pl['name'], pl['external_urls']['spotify']) for pl in playlists['items']]
    playlists_html = '<br>' .join([f'{name}: {url}' for name, url in playlists_info])
    
    return playlists_html

# last endpoint we are creating is the log out endpoint
# clearing the session, compeletely removing the access token and everything else in the session so that the user is forced to log in again
# not needed but added to highlight that logout works and that a user will need to login again to use this application

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# telling python that when we run this app, 
# either this is the first line of code 
# or we want to run everything in this block
if __name__ == '__main__':
    app.run(debug=True) 
    # enables: as we make changes to the code and save these changes, it will restart the service, so we do not have to do that manually 
