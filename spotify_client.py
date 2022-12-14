#        SPOTIFY_CLIENT.py
# ---------------------------------
# Class that is used to make working with the Spotify API easier. Much of the Spotify
# API does not have a structured client in order to directly access the API, so this class
# creates one and makes it so that making API calls is easy. This automatically gets access
# tokens, but you must set up your own Spotify Developers App with your own client
# secret and client id in order to use the service. This is done so that one can not make
# function calls with the app tied to this ID. This class can get the list of a user's playlist
# from their username and create search terms for youtube. This program also allows
# the user to select which playlist they want to choose and directly convert one playlist
# from Spotify to one playlist on Youtube.
import datetime
import requests
import base64

class SpotifyAPI(object):
    access_token = None
    expiration_of_token = datetime.datetime.now
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret):
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret

    # INPUTS: NONE
    # OUTPUTS: The base64
    # DESC: Creates the base64 string that is used with get_token_header(). In order to get access 
    #       token to Spotify API client ID and client secret must be encoded as base64 and then 
    #       decoded in order to get token from API
    def get_client_cred(self):
        client_id = self.client_id
        client_secret = self.client_secret
        if client_id == None or client_secret == None:
            raise Exception("Must set client ID and client Secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode() #DO DECODE HERE TO MAKE NOT A b"string"

    # INPUTS: NONE
    # OUTPUTS: creates header for authorization token
    # DESC: Creates the authorization header that is used in get_access_token(). Calls get_client_cred()
    #       to get base64 encoded string in order to format access token call. returns the headers
    #       that will be used to call the Spotify API and get an access token
    def get_token_header(self):
        token_headers = {
            "Authorization" : f"Basic {self.get_client_cred()}"
        }
        return token_headers

    # INPUTS: NONE
    # OUTPUTS: creates data for authorization token
    # DESC: Creates the authorization data that is used in get_access_token(). Returns the headers
    #       that will be used to call the Spotify API and get an access token.
    def get_token_data(self):
        token_data = {
            "grant_type" : "client_credentials"
         }    
        return token_data

    # INPUTS: NONE
    # OUTPUTS: boolean on if the token is expired
    # DESC: Checks if the token that the spotify client is currently using is expired
    #       Used to see if need to refresh client's token before making function calls.
    def token_is_expired(self):
        return self.expiration_of_token < datetime.datetime.now()
    
    # INPUTS: NONE
    # OUTPUTS: True if authorization token is usable, False if not
    # DESC: Creates and gets the authorization token that is used in every request call.
    #       Also updates the time of the expiration of the token which can be used later in order
    #       to make sure that the token is usuable by the API. 
    #       WARNING: User ID and User Secret MUST be set in order to use this function. Will throw 
    #       error if self.client_id and self.client_secret is not set
    def get_access_token(self):
        r = requests.post(self.token_url, data=self.get_token_data(), headers=self.get_token_header())
        if r.status_code not in range(200,299):
            return False
        data = r.json()
        now = datetime.datetime.now()
        self.access_token = data["access_token"]
        expire_time = data["expires_in"]
        self.expiration_of_token = now + datetime.timedelta(seconds=expire_time)
        return True

    # INPUTS: NONE
    # OUTPUTS: header for authorization to be included with requests
    # DESC: Creates the authorization header that is required for many requests in spotify API.
    #       Creates a dictionary with form "Bearer {accesstoken} as value". AUTOMATICALLY checks
    #       if authorization token is expired or not, so can assume if calling this function that
    #       you will be provided with a non-expired authorization token
    def get_authorization_header(self):
        if self.token_is_expired():
            self.get_access_token()
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        return headers

    # INPUTS: user ID to look up playlists for(str)
    # OUTPUTS: list of playlists titles
    # DESC: Takes a user ID and returns the title of all of the playlists. Form of the return of the get requests .json()
    #       is a dictionary in which ['items'] contains the data for all of the playlists. In order to get each playlist,
    #       we iterate through all of list in json_playlists['items] and then pull the name from that dictionary.
    #       Each playlist is a item in the json_playlists['items'] list. This only can get playlists that a user has public.
    #       Used in order to display to user which playlist they want to choose. Much easier to choose from list of playlist
    #       than from a specific playlist ID, even though API uses exclusively playist Id's.
    def get_playlists_name_user(self, user):
        headers = self.get_authorization_header() #Automatically detects if bad token
        endpoint = f"https://api.spotify.com/v1/users/{user}/playlists"
        playlists = requests.get(endpoint, headers=headers).json()
        playlist_name_list = []
        for i in range(len(playlists['items'])):
            playlist_name_list.append(playlists['items'][i]['name'])
        return playlist_name_list

    # INPUTS:  playlist ID to look up artist (str)
    # OUTPUTS: list of artists in order in givne playlist
    # DESC: Takes the ID of a playlist and returns all of the artists in that playlist in order
    #       of the songs on the playlists. Artists can be repeated. 
    #       WARNING!!!: By spotify API, the maximum return for this request is 100 songs. If you playlsit has more than 100 songs
    #       you can not use this function to get each song. It will only return the first 100. 
    #       Due to the limitations of the Youtube API, do not need more than 100 calls now
    def get_artists_from_playlist_id(self, playlist_id):
        headers = self.get_authorization_header() #Automatically detects if bad token
        endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        raw_dict_artists_in_playlist = requests.get(endpoint, headers=headers).json()
        artists_in_playlist = []
        for i in range(len(raw_dict_artists_in_playlist['items'])):
            artists_in_playlist.append(raw_dict_artists_in_playlist['items'][i]['track']['artists'][0]['name'])
        return artists_in_playlist

    # INPUTS: user ID to look up playlists for (str)
    # OUTPUTS: list of playlists ID's
    # DESC: Takes a user ID and returns the ID of all of the playlists. Form of the return of the get requests .json()
    #       is a dictionary in which ['items'] contains the data for all of the playlists. In order to get each playlist,
    #       we iterate through all of list in json_playlists['items] and then pull the id from that dictionary.
    #       Each playlist is a item in the json_playlists['items'] list. This only can get playlists that a user has public.
    def get_playlists_id_user(self, user):
        headers = self.get_authorization_header() #Automatically detects if bad token
        endpoint = f"https://api.spotify.com/v1/users/{user}/playlists"
        playlists = requests.get(endpoint, headers=headers).json()
        playlist_id_list = []
        for i in range(len(playlists['items'])):
            playlist_id_list.append(playlists['items'][i]['id'])
        return playlist_id_list

    # INPUTS:  playlist ID to look up artist (str)
    # OUTPUTS: dictionary with name of playlist as key and its playlistID as value
    # DESC: Takes the user and makes a dictionary of all of the playlist's titles and 
    #       the id of each playlist. Is used to display to user so user knows which 
    #       playlist they are choosing. Calls get_playlists_name_user and 
    #       get_playlists_id_user in order to handle this.
    def make_dict_playlistname_playlistid_from_user(self, user):
        playlist_name = self.get_playlists_name_user(user)
        playlist_id = self.get_playlists_id_user(user)
        ret_dict = {}
        for i in range(len(playlist_name)):
            ret_dict[playlist_name[i]] = playlist_id[i]
        return ret_dict

    # INPUTS:  playlist ID to look up artist (str)
    # OUTPUTS: list of artists in order in givne playlist
    # DESC: Takes the ID of a playlist and returns all of the artists in that playlist in order
    #       of the songs on the playlists. Artists can be repeated. 
    #       WARNING!!!: By spotify API, the maximum return for this request is 100 songs. If you playlsit has more than 100 songs
    #       you can not use this function to get each song. It will only return the first 100. 
    #       Due to the limitations of the Youtube API, do not need more than 100 calls now
    def get_artists_from_playlist_id(self, playlist_id):
        headers = self.get_authorization_header() #Automatically detects if bad token
        endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        raw_dict_artists_in_playlist = requests.get(endpoint, headers=headers).json()
        num_tracks = raw_dict_artists_in_playlist['total']
        artists_in_playlist = []
        offset = 0
        while len(artists_in_playlist) < num_tracks:
            for i in range(len(raw_dict_artists_in_playlist['items'])):
                artists_in_playlist.append(raw_dict_artists_in_playlist['items'][i]['track']['artists'][0]['name'])
            if num_tracks > 100:
                offset += 100
                endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset={offset}"
                raw_dict_artists_in_playlist = requests.get(endpoint, headers=headers).json()
        return artists_in_playlist