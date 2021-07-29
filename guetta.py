import glob
import os
from pathlib import Path
from lxml import etree as et
import xml.dom.minidom as minidom

jellyfinPlaylistDir="/media/stroblme/hauco/jellyfin/data/playlists"
# jellyfinPlaylistDir="/media/stroblme/hauco/guetta"
playlistDir=Path("/media/veracrypt1/system/playlists")

for playlist in playlistDir.glob("*.m3u"):
    name = playlist.stem

    match = glob.glob(jellyfinPlaylistDir+"/"+name+"/playlist.xml")
    if match == []:
        continue

    print(f"Processing Playlist: {name}")

    jellyfinPlaylist = et.parse(match[0])

    jellyfinSongs = list()

    for neighbor in jellyfinPlaylist.iter('Path'):
        jellyfinSongs.append(neighbor.text)

    print(f"Found {len(jellyfinSongs)} songs in the xml playlist")

    with open(playlist, 'r') as f:
        songs = f.readlines()

    print(f"Found {len(songs)} songs in the m3u playlist")
    

    playlistRoot=jellyfinPlaylist.find('PlaylistItems')
    if playlistRoot == None:
        itemRoot = jellyfinPlaylist.getroot()
        playlistRoot = et.SubElement(itemRoot, 'PlaylistItems')
    for song in songs:
        if song in jellyfinSongs:
            continue
        tempItem = et.SubElement(playlistRoot,'PlaylistItem')
        tempPath = et.SubElement(tempItem,'Path')
        tempPath.text = song
    
    xmlstr = minidom.parseString(et.tostring(jellyfinPlaylist)).toprettyxml()
    xmlstr = xmlstr.replace('\n</Path>', '</Path>')
    xmlstr = xmlstr.replace('\t\t\t\n', '')
    xmlstr = xmlstr.replace('\t\t\n', '')
    xmlstr = xmlstr.replace('\t\n', '')

    try:
        
        with open(match[0], "w") as f:
            f.write(xmlstr)
    except Exception as e:
        print(f"Cannot write to file {match[0]}")
    # jellyfinPlaylist.write(match[0], pretty_print=True)

