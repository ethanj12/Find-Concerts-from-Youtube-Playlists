from textwrap import indent
import spotify_client
import stubhub_client_file
import os
import requests

# INPUTS:  None
# OUTPUTS: returns spotify_client object used to make API calls
# DESC: Must set your spotify secret and and spotify client ID's in the environment 
#       of your computer. A easy tutorial for this in windows is here:
#       https://www.youtube.com/watch?v=IolxqkL7cD8&ab_channel=CoreySchafer
#       Spotify does not have a structured way client, so we have to create our
#       own in order to model API calls. In order to get Spotify ID and 
#       a Spotify secret, follow the tutorial in the readme of the repository.
def get_spotify_client():
    spotify_client_id = os.environ.get("spotify_api_client_id")
    spotify_client_secret = os.environ.get("spotify_api_client_secret")
    spotify = spotify_client.SpotifyAPI(client_id=spotify_client_id, client_secret=spotify_client_secret)
    
    spotify.get_access_token()  # Needed to make API calls

    return spotify

# INPUTS:  message for console for input, target type of input
# OUTPUTS: an input from user with type "type"
# DESC: Gets an input from the user and returns the input in the 
#       type that is passed to it. For this project, the only two
#       types that we need from the user and int and string, but we could easily
#       extend this if we needed more types.
def get_user_input(message, type):
    ret = input(message)
    if type == "int": #Do not have to worry if type == str, input returns a str
        try:
            ret = int(ret)
            return ret
        except:
            print("Please enter an integer")
            get_user_input(message, type)
    return ret

# INPUTS:  username to look up on spotify
# OUTPUTS: returns list with index 0 being id and index 1 being name of playlist
#          (not a tuple in case in future, want more info about playlist in this call)
# DESC: This logic handles selecting the playlist from the user's all available playlist
#       and then getting the ID and the name of that playlist. The user will ahve a choice
#       between all of their avaiable playlist, and the choices and their corresponding
#       index will be printed to the screen. The user then selects a playlist, and the
#       spotify_client object then gets the ID and the name of the playlist from the list
#       that was returned with the original call of make_dict_playlistname_playlistid_from_user()
def get_playlist_of_user(username):
    id_playlists_of_user = spotify_client.get_playlists_id_user(f"{username}")
    dict_playlist_name_to_id = spotify_client.make_dict_playlistname_playlistid_from_user(username)
    list_of_playlist_names = spotify_client.get_playlists_name_user(username)

    option_value = 1
    for key in dict_playlist_name_to_id:
        print(f"{key}-{option_value}")
        option_value += 1
    playlist_selection = get_user_input("Which playlist would you like to pick (number): ", "int")

    spotify_playlist_id = str(id_playlists_of_user[playlist_selection - 1])
    spotify_playlist_name = str(list_of_playlist_names[playlist_selection - 1])
    playlist_id_and_playlist_name = [spotify_playlist_id, spotify_playlist_name]
    return playlist_id_and_playlist_name

def sort_by_date(e):
    return e[0]

def print_list_of_concerts(concert_list):
    for i in range(len(concert_list)):
        concert = concert_list[i]
        print(f"{concert[1]} - {concert[2]}, {concert[3]} on {concert[0]} - {concert[4]}")

def main():
    global spotify_client
    spotify_client = get_spotify_client()
    #username = get_user_input("Username: ", str)
    spotify_playlist_to_search = get_playlist_of_user("coolethan12")
    artists = spotify_client.get_artists_from_playlist_id(spotify_playlist_to_search[0])
    artists = list(set(artists)) #Gets rid of duplicates but does not preserve order

    stubhub_client = stubhub_client_file.StubHubAPI()
    list_of_concerts = []
    list_of_artists_problems = []
    for artist in artists[:50]:
        search_params = {
            'apikey': '6GAvtS8RedAF2GKdb7qNyWIPuj7l4RVf',
            'keyword': f"{artist}"
        }

        response = requests.get('https://app.ticketmaster.com/discovery/v2/events', params=search_params).json()

        if 'page' in response.keys() and response['page']['totalElements'] == 0:
            print(f"There are no events for artist {artist}")
            list_of_artists_problems.append(artist)
            continue
        if not '_embedded' in response.keys():
            print(f"_embedded not found first for {artist}")
            list_of_artists_problems.append(artist)
            continue
        if not 'events' in response['_embedded'].keys():
            print(f"No events found for {artist}")
            list_of_artists_problems.append(artist)
            continue
        response = response['_embedded']['events'] #Subset to just all events. Trims all extraneous   
        for i in range(len(response[:15])): #First 5 events for each artist
            single_event = response[i]
            if not 'name' in single_event.keys():
                print(f"No name found for this event of {artist}")
                list_of_artists_problems.append(artist)
                continue
            name_of_event = single_event['name']
            if not '_embedded' in single_event.keys():
                print(f"No name found for this event of {artist}, {name_of_event}")
                list_of_artists_problems.append(artist)
                continue
            single_event_embedded = single_event['_embedded']

            if not 'venues' in single_event_embedded.keys():
                print(f"No venue found for this event of {artist}, {name_of_event}")
                list_of_artists_problems.append(artist)
                continue
            city_of_event = single_event_embedded['venues'][0]['city']['name']
            country_code_of_event = single_event_embedded['venues'][0]['country']['countryCode']
            state_of_event = ""
            if country_code_of_event == "US":
                state_of_event = single_event_embedded['venues'][0]['state']['stateCode']
            

            date_time_event = None
            if 'localDate' in single_event['dates']['start'].keys():
                date_time_event = single_event['dates']['start']['localDate']
            if date_time_event != None:
                list_of_concerts.append((date_time_event, name_of_event, f"{city_of_event}, {state_of_event}", country_code_of_event, artist))
            else:
                print(single_event['dates'])
                print(f"Date and time not selected yet for this event of {artist}, {name_of_event}")

    list_of_concerts.sort(key=sort_by_date)
    print_list_of_concerts(list_of_concerts)
    # print(list_of_artists_problems)

if __name__ == '__main__':
    main()

