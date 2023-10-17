#!/usr/bin/env python

from tinydb import TinyDB
import tidalapi

DBASE="playlist.json"

session = tidalapi.Session()

# Wait for device to be linked by user
session.login_oauth_simple()

playlists = session.user.playlists()

db = TinyDB(DBASE)

for p in db:
    playlist_name = p["name"]
    insert_tracks = p["tracks"]
    print(f'Importing playlist: {playlist_name}')
     
    playlist = list(filter(lambda p: p.name == playlist_name, playlists))

    if playlist:
        playlist = playlist[0]
    else:
        playlist = session.user.create_playlist(playlist_name, "")
    
    trackset = set([t.id for t in playlist.tracks()])
    
    for t in insert_tracks:
        if 'id' in t and t['id'] not in trackset:
            playlist.add([t['id']])
    

db.close()
