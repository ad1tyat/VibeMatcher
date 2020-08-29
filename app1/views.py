import requests
from django.shortcuts import render
import base64
import datetime
from urllib.parse import urlencode
from django.views.generic import TemplateView
from app1.forms import HomeForm

# Create your views here.


# get them from https://developer.spotify.com/dashboard/login

client_id = "---"
client_secret = "---"


class SpotifyAPI(object):
    access_token = None
    access_token_did_expire = True
    access_token_expires = datetime.datetime.now()
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credentials(self):
        """
        Returns a base64 encoded string
        """
        client_id = self.client_id
        client_secret = self.client_secret

        if client_id == None or client_secret == None:
            raise Exception("client id or secret is wrong")

        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {"Authorization": f"Basic {client_creds_b64}"}

    def get_token_data(self):
        return {
            "grant_type": "client_credentials",
        }

    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(token_url, data=token_data, headers=token_headers)

        if r.status_code not in range(200, 299):
            return False
        data = r.json()
        now = datetime.datetime.now()
        self.access_token = data["access_token"]
        expires_in = data["expires_in"]
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True


def index(request):
    spotify = SpotifyAPI(client_id, client_secret)
    spotify.perform_auth()
    access_token = spotify.access_token

    headers = {"Authorization": f"Bearer {access_token}"}
    endpoint = "https://api.spotify.com/v1/search"
    data = urlencode({"q": "Time", "type": "track"})

    lookup_url = f"{endpoint}?{data}"
    r = requests.get(lookup_url, headers=headers)
    print(r.json())
    return render(request, "app1/base.html")


class UserProfile:
    def __init__(self, items):
        self.items = items

    def __str__(self):
        for artist in self.items:
            print(artist["images"]["name"])


class HomeView(TemplateView):
    template_name = "app1/home.html"

    def get(self, request):
        form = HomeForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = HomeForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data["track_name"]
        x = text
        spotify = SpotifyAPI(client_id, client_secret)
        spotify.perform_auth()
        access_token = spotify.access_token

        headers = {"Authorization": f"Bearer {access_token}"}
        endpoint = "https://api.spotify.com/v1/search"
        data = urlencode({"q": x, "type": "track"})

        lookup_url = f"{endpoint}?{data}"
        r = requests.get(lookup_url, headers=headers)

        data = r.json()
        tracks = data["tracks"]["items"][0]["artists"][0]["external_urls"]["spotify"]
        return render(request, "app1/base.html", {"track_name": x, "link": tracks})

