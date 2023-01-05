from requests import get
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth


class Hot100toSpoti:
    def __init__(self):
        self.date = None
        self.artists_list = None
        self.songs_list = None
        self.CLIENT_ID =
        self.CLIENT_SECRET =
        self.REDIRECT_URI =
        self.SCOPE = "playlist-modify-public"
        self.song_uris = []

    def give_date(self):
        self.date = str(input("Type a date that you want to get TOP100 songs from. (YYYY-MM-DD):\n"))

    def scrape_bilboard(self):
        url = f"https://www.billboard.com/charts/hot-100/{self.date}/#"
        rspns = get(url).text
        soup = BeautifulSoup(rspns, "html.parser")
        songs_tags = soup.find_all(name="h3", class_="a-no-trucate")
        self.songs_list = [song.getText().replace("\n", "").replace("\t", "").replace("(", "").replace(")", "")
                               .replace("'", "").replace('"', "") for song in songs_tags]
        artists_tag = soup.find_all(name="span", class_="a-no-trucate")
        self.artists_list = [artist.getText().replace("\n", "").replace("\t", "")
                                 .replace(".", "") for artist in artists_tag]

    def spoti(self):
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                scope=self.SCOPE,
                redirect_uri=self.REDIRECT_URI,
                client_id=self.CLIENT_ID,
                client_secret=self.CLIENT_SECRET,
                show_dialog=True,
                cache_path="token.txt"
            )
        )
        user_id = sp.current_user()["id"]

        year = self.date.split("-")[0]

        for i in range(100):
            artist = self.artists_list[i]

            title = self.songs_list[i]

            result = sp.search(q=f"artist:{artist} track:{title} year:{year}", type="track", )
            try:
                uri = result["tracks"]["items"][0]["uri"]
                self.song_uris.append(uri)
                # print(f"{artist} - {title} found in Spotify. Added to list.")
            except IndexError:
                result = sp.search(q=f"artist:{artist} track:{title}", type="track", )
                try:
                    uri = result["tracks"]["items"][0]["uri"]
                    self.song_uris.append(uri)
                except IndexError:
                    pass

        list_name = f"Top 100 from {self.date}"
        list_description = f"Top 100 from {self.date}. Enjoy!"

        new_list = sp.user_playlist_create(user=user_id, name=list_name,
                                           description=list_description, public=True, collaborative=False)

        list_id = new_list["id"]

        sp.playlist_add_items(list_id, items=self.song_uris)
