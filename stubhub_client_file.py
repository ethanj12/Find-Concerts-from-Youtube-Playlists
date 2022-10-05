import requests
import base64




class StubHubAPI(object):
    access_token = None
    client_id = "CpVQMWACXMCo4gGHnypJLbQkCydcLSpx"
    client_secret = "hOQeAX8IUADeRTk6"
    token_url = "https://accounts.spotify.com/api/token"
    access_token = None

    def __init__(self):
        super().__init__()
        self.client_id = self.client_id
        self.client_secret = self.client_secret

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
    # OUTPUTS: header for authorization to be included with requests
    # DESC: Creates the authorization header that is required for many requests in spotify API.
    #       Creates a dictionary with form "Bearer {accesstoken} as value". AUTOMATICALLY checks
    #       if authorization token is expired or not, so can assume if calling this function that
    #       you will be provided with a non-expired authorization token
    def get_authorization_header(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            'Accept': 'application/json',
        }
        return headers

    def get_auth_token(self):
        headers = {
                    'Authorization': f'Basic {self.get_client_cred()}',
                  }
        params = {
                    'grant_type': 'client_credentials',
                 }
        json_data = {
                    'username': 'frickthepledges2022@gmail.com',
                    'password': 'Ilikegiraffes12!',
                    }
        response = requests.post('https://api.stubhub.com/sellers/oauth/accesstoken', params=params, headers=headers, json=json_data)
        self.access_token = response.json()["access_token"]
        return self.access_token
        
    def search_performers(self, list_of_artists):
        headers = self.get_authorization_header()
        endpoint = 'https://api.stubhub.com/sellers/search/events/v3'
        params = {
            "q" : "Beach Bunny"
        }

        response = requests.get('https://api.stubhub.com//partners/search/performers/v3/', params=params, headers=headers)
        return response.json()

