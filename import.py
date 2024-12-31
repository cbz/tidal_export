#!/usr/bin/env python

import argparse
from tinydb import TinyDB
import tidalapi
import difflib

DBASE = "playlist.json"
VERBOSE = False


#
# Process a track we have to search for
def process_searchable_track(playlist, trackset, t):
    artist = t["artist"]
    album = t["album"]
    track = t["track"]
    search_results = session.search(query=f"{artist} {track}", models=[tidalapi.Track])

    tracks = search_results["tracks"]

    if not tracks:
        print(f"Couldn't find track: {artist} - {track}")
        return

    # Track ids in results
    searchset = set([t.id for t in tracks])

    # Check whether the track is already in the playlist
    if not trackset.intersection(searchset):
        newtrack = False
        if len(tracks) == 1:
            newtrack = tracks[0]
        else:
            closest_albums = difflib.get_close_matches(album, [t.album.name for t in tracks],cutoff=0.5)
            tracks = [t for name in closest_albums for t in tracks if t.album.name == name]
            closest_tracks = difflib.get_close_matches(track, [t.name for t in tracks])
            tracks = [t for name in closest_tracks for t in tracks if t.name == name]

            if tracks:
                newtrack = tracks[0]

        if newtrack:

            if VERBOSE:
                print("Added track: {0} - {1} - {2}".format(
                    newtrack.artist.name, newtrack.album.name, newtrack.name))

            playlist.add([newtrack.id])
            trackset.add(newtrack.id)


def process_playlists(database, playlists):

    with TinyDB(database) as db:
        for p in db:
            playlist_name = p["name"]
            description = ""
            if "description" in p:
                description = p["description"]

            insert_tracks = p["tracks"]
            print(f"Importing playlist: {playlist_name}")

            playlist = list(filter(lambda p: p.name == playlist_name, playlists))

            if playlist:
                playlist = playlist[0]
            else:
                playlist = session.user.create_playlist(playlist_name, description)

            trackset = set([t.id for t in playlist.tracks()])

            for t in insert_tracks:
                if 'id' in t and t['id'] == "":
                    process_searchable_track(playlist, trackset, t)
                    continue
                if 'id' in t and t['id'] not in trackset:
                    playlist.add([t['id']])
                    trackset.add(t['id'])
                    continue


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Imports playlist database into Tidal")
    parser.add_argument("-v", "--verbose", action="store_true")  # on/off flag
    parser.add_argument("database", nargs="?", default=DBASE)

    arguments = parser.parse_args()
    VERBOSE = arguments.verbose

    session = tidalapi.Session()

    # Wait for device to be linked by user
    session.login_oauth_simple()

    playlists = session.user.playlists()

    process_playlists(arguments.database, playlists)
