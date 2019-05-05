import sys
import os
import re
import json
import time
from pprint import PrettyPrinter as pp
# PyQt5 Libraries
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from SpotifyWidget import *
# Spotify API Library
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
# Image library
import imageio
from scipy import ndimage, spatial
from PIL import Image, ImageDraw
import PIL as pillow
import requests
from io import BytesIO
import numpy as np

# Spotify API ID and Key
# CLIENTID = "2c63ae3585d34835b04b34971282a731"
# CLIENTSECRET = "ed953ad432654ed796e9083db7174639"

class SpotifyWidget(QMainWindow, Ui_SpotifyWidget):
    def __init__(self, parent=None):
        super(SpotifyWidget, self).__init__(parent)
        self.setupUi(self)

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

        # Connect UI components to methods
        self.pausePlay.clicked.connect(self.pausePlayPressed)
        self.nextPB.clicked.connect(self.nextPressed)
        self.prevPB.clicked.connect(self.prevPressed)
        self.volSlider.valueChanged.connect(self.volSliderMoved)
        self.changeDeviceCombo.currentIndexChanged.connect(self.deviceComboIndexChanged)
        self.searchEdit.textEdited.connect(self.searching)

        # Set profile picture
        cp = self.sp.current_user()
        profileImageURL = cp["images"][0]["url"]
        response = requests.get(profileImageURL)
        img = Image.open(BytesIO(response.content))
        imageio.imwrite('profilePhoto.png', img)
        pixmap = QPixmap("profilePhoto.png")
        self.profileLabel.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.FastTransformation))
        self.userInfoLabel.setText(cp["display_name"])

        # Device options QComboBox
        self.populateDeviceComboboxes()
        self.updateCurrentTrack()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.checkForSongChange)
        self.timer.start(2000) #trigger every 2 secs

    def checkForSongChange(self):
        currTmp = self.sp.currently_playing()
        if(currTmp["item"]["id"] != self.currentTrackID):
            self.updateCurrentTrack()

    def deviceComboIndexChanged(self):
        deviceReq = self.changeDeviceCombo.currentText()
        allDevs = self.sp.devices()
        for d in allDevs["devices"]:
            if d["name"] == deviceReq:
                self.currentDeviceID = d["id"]
                break
        self.sp.transfer_playback(self.currentDeviceID)
        return

    def volSliderMoved(self):
        self.volume = int(self.volSlider.value())
        self.sp.volume(self.volume)
        return

    def nextPressed(self):
        self.sp.next_track()
        self.updateCurrentTrack()
        return

    def prevPressed(self):
        self.sp.previous_track()
        self.updateCurrentTrack()
        return

    def populateDeviceComboboxes(self):
        devices = self.sp.devices()
        deviceNames = [ d["name"] for d in devices["devices"] ]
        self.changeDeviceCombo.addItems(deviceNames)

        allDevs = self.sp.devices()
        for d in allDevs["devices"]:
            if d["is_active"] == True:
                for i in range(self.changeDeviceCombo.maxCount()):
                    if(self.changeDeviceCombo.itemText(i) == d["name"]):
                        self.changeDeviceCombo.setCurrentIndex(i)
                        break
                self.currentDeviceID = d["id"]
                break
        return

    def updateCurrentTrack(self):
        currentData = self.sp.currently_playing()
        self.playingNow = currentData["is_playing"]
        self.currentTrack = (currentData["item"]["name"],
                             currentData["item"]["album"]["artists"][0]["name"])
        albumArtURL = currentData["item"]["album"]["images"][0]["url"]
        self.currentTrackID = currentData["item"]["id"]
        response = requests.get(albumArtURL)
        img = Image.open(BytesIO(response.content))
        imageio.imwrite('albumArtPhoto.png', img)
        pixmap = QPixmap("albumArtPhoto.png")
        self.albumArtLabel.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.FastTransformation))
        self.trackTitleLabel.setText(self.currentTrack[0])
        self.trackArtistLabel.setText(self.currentTrack[1])

    def pausePlayPressed(self):
        if(self.playingNow == True):
            self.sp.pause_playback()
            self.playingNow = False
        else:
            self.sp.start_playback()
            self.playingNow = True
        return

    def searching(self):
        query = self.searchEdit.text()
        results = self.sp.search(query, limit=3, offset=0, type='track')
        for i in results["tracks"]["items"]:
            print(i["name"])





if __name__ == "__main__":
    currentApp = QApplication(sys.argv)
    currentForm = SpotifyWidget()
    currentForm.show()
    currentApp.exec_()
