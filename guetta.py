import glob
import os
import subprocess
from pathlib import Path
from lxml import etree as et
import xml.dom.minidom as minidom

jellyfinPlaylistDir=Path("/media/stroblme/hauco/jellyfin/data/playlists")
# jellyfinPlaylistDir="/media/stroblme/hauco/guetta"
playlistDir=Path("/media/veracrypt1/system/playlists")
mobileDir=Path("/media/veracrypt1/system/sync")
musicDir=Path("/media/veracrypt1/music")

def jellyfinPlaylistSync():

    for playlist in playlistDir.glob("*.m3u"):
        name = playlist.stem

        match = glob.glob(jellyfinPlaylistDir.absolute().as_posix()+"/"+name+"/playlist.xml")
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

def mobilePlaylistSync():
    for playlist in playlistDir.glob("*.m3u"):
        name = playlist.stem

        match = glob.glob(jellyfinPlaylistDir.absolute().as_posix()+"/"+name+"/playlist.xml")
        if match == []:
            continue

        print(f"Processing Playlist: {name}")

        with open(playlist, 'r') as f:
            songs = f.readlines()

        print(f"Found {len(songs)} songs in the m3u playlist")
        

        for song in songs:
            songPath = song.replace("\n","")
            songName = songPath.replace(musicDir.absolute().as_posix()+"/","")

            fullPath = Path(mobileDir.absolute().as_posix()+"/"+songName)
            os.makedirs(fullPath.parent.as_posix(), exist_ok=True)

            if songName.endswith(".mp3"):
                try:
                    subprocess.run(f'/bin/cp -u "{songPath}" "{mobileDir.absolute().as_posix()}/{songName}"', shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    print(e)
                    continue
            else:
                try:
                    # os.symlink(songPath,symlinkDir.absolute().as_posix()+"/"+songName)
                    subprocess.run(f'/usr/bin/ffmpeg -i "{songPath}" -ar 44100 -b:a 320000 -ac 2 -n "{mobileDir.absolute().as_posix()}/{songName}"', shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    print(e)
                    continue

        syncPlaylist = playlist.absolute().as_posix().replace(playlistDir.absolute().as_posix(), mobileDir.absolute().as_posix())
        with open(syncPlaylist, 'w+') as f:
            for song in songs:
                songRemap = song.replace(musicDir.absolute().as_posix(), ".")
                f.write(songRemap)

# jellyfinPlaylistSync()
mobilePlaylistSync()