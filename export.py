#!/usr/bin/env python

from tinydb import TinyDB
import tidalapi

DBASE="playlist.json"

session = tidalapi.Session()

# Will print a prompt to link the device
session.login_oauth_simple()

playlists = session.user.playlists()

# Sort playlists in order - so that they go back into tidal in the correct order
playlists.sort(key=lambda x: x.last_updated)

db = TinyDB(DBASE)

for p in playlists:
    print(f'Exporting playlist: {p.name}')
    playlist = { 'name': p.name }
    
    tracks = []
    for t in p.tracks():
        tracks.append({'artist': t.artist.name, 'album': t.album.name, 'track': t.name, 'id': t.id})

    playlist['tracks'] = tracks

    db.insert(playlist)

db.close()
