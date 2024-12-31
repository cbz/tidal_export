#!/usr/bin/env python

import argparse
from tinydb import TinyDB
import tidalapi
import json

DBASE="playlist.json"
VERBOSE = False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Exports playlist database from Tidal')
    parser.add_argument("-v", "--verbose", action="store_true")  # on/off flag
    parser.add_argument('database', nargs='?', default=DBASE)

    arguments = parser.parse_args()
    VERBOSE = arguments.verbose
    
    session = tidalapi.Session()

    # Will print a prompt to link the device
    session.login_oauth_simple()

    playlists = session.user.playlists()

    # Sort playlists in order - so that they go back into tidal in the correct order
    playlists.sort(key=lambda x: x.last_updated)

    with TinyDB(arguments.database) as db:

        for p in playlists:
            print(f'Exporting playlist: {p.name}')
            playlist = { 'name': p.name, 'description': p.description }
            
            tracks = []
            for t in p.tracks():
                tracks.append({'artist': t.artist.name, 'album': t.album.name,
                               'track': t.name, 'id': t.id})

            playlist['tracks'] = tracks
            db.insert(playlist)
