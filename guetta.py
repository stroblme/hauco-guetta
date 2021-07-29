import glob
import os
from pathlib import Path
import xml.etree.ElementTree as et

jellyfinPlaylistDir="/media/stroblme/hauco/jellyfin/data/playlists"
# jellyfinPlaylistDir="/media/stroblme/hauco/guetta"
playlistDir=Path("/media/veracrypt1/system/playlists")

for playlist in playlistDir.glob("*.m3u"):
    name = playlist.stem

    match = glob.glob(jellyfinPlaylistDir+"/"+name+"/playlist.xml")
    if match == []:
        continue

    jellyfinPlaylist = et.parse(match[0])

    jellyfinSongs = list()

    for neighbor in jellyfinPlaylist.iter('Path'):
        jellyfinSongs.append(neighbor.text)

    print(f"Found {len(jellyfinSongs)} songs in the xml playlist")

    with open(playlist, 'r') as f:
        songs = f.readlines()

    print(f"Found {len(songs)} songs in the m3u playlist")
    

    playlistRoot=jellyfinPlaylist.find('PlaylistItems')
    for song in songs:
        if song in jellyfinSongs:
            continue
        tempItem = et.SubElement(playlistRoot,'PlaylistItem')
        tempPath = et.SubElement(tempItem,'Path')
        tempPath.text = song


    jellyfinPlaylist.write(match[0])

