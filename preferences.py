import sys
import os
import re
import json
import time
from pprint import PrettyPrinter as pp
# Spotify API Library
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
# Image library
import imageio
import requests
from io import BytesIO
import numpy as np

# Spotify API ID and Key
# CLIENTID = "2c63ae3585d34835b04b34971282a731"
# CLIENTSECRET = "ed953ad432654ed796e9083db7174639"

class Personalization:
    def __init__(self, parent=None):
        # Spotify initialization
        scope = 'user-read-private user-read-playback-state user-modify-playback-state user-top-read playlist-modify-private playlist-modify-public'
        redirect_uri = "http://localhost:8888/callback/"
        username = "andrew.stpierre3131"
        token = util.prompt_for_user_token(username,
                                           scope,
                                           redirect_uri=redirect_uri)
        self.sp = spotipy.Spotify(auth=token)
        self.sp.trace = False

        # Class member variables
        self.playingNow = False
        self.volume = 0
        self.currentTrackID = 0
        self.genres = {}
        self.topTrackList = {}
        self.topArtistList = {}

        # Method calls
        self.topTrackList["short_term"] = []
        self.topTrackList["medium_term"] = []
        self.topTrackList["long_term"] = []

        self.topTracks(term="short")
        self.topTracks(term="medium")
        self.topTracks(term="long")

        self.topArtistList["short_term"] = []
        self.topArtistList["medium_term"] = []
        self.topArtistList["long_term"] = []

        self.topArtists(term="short")
        self.topArtists(term="medium")
        self.topArtists(term="long")

        self.processPreferences()

        #print(self.topTrackList)

    def topTracks(self, term=None):
        if(term==None):
            term="long_term"
        elif("short" in term):
            term="short_term"
        elif("medium" in term):
            term="medium_term"
        elif("long" in term):
            term="long_term"
        else: term="long_term"

        results= self.sp.current_user_top_tracks(limit=100, offset=0, time_range=term)

        for i in results["items"]:
            self.topTrackList[term].append([i["id"], i["name"], i["artists"][0]["name"], i["artists"][0]["id"]])

        return

    def topArtists(self, term=None):
        if(term==None):
            term="long_term"
        elif("short" in term):
            term="short_term"
        elif("medium" in term):
            term="medium_term"
        elif("long" in term):
            term="long_term"
        else: term="long_term"

        results= self.sp.current_user_top_artists(limit=100, offset=0, time_range=term)

        for i in results["items"]:
            self.topArtistList[term].append([i["id"], i["name"], i["genres"]])

        return

    def processPreferences(self):
        genreResults = {}
        for a in self.topArtistList["short_term"]:
            for g in a[2]:
                if g not in genreResults:
                    genreResults[g] = [a[1]]
                else:
                    genreResults[g].append(a[1])
        for genre in genreResults:
            if "country" in genre:
                print(genre, genreResults[genre], "\n")



    def searching(self):
        query = self.searchEdit.text()
        results = self.sp.search(query, limit=3, offset=0, type='track')
        for i in results["tracks"]["items"]:
            print(i["name"])





if __name__ == "__main__":
    mySpotify = Personalization()
