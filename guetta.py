import glob
import os
import subprocess
from pathlib import Path
from lxml import etree as et
import xml.dom.minidom as minidom
import eyed3

jellyfinPlaylistDir=Path("/media/stroblme/hauco/jellyfin/data/playlists")
# jellyfinPlaylistDir="/media/stroblme/hauco/guetta"
playlistDir=Path("/media/veracrypt1/system/playlists")
mobileDir=Path("/media/veracrypt1/system/sync")
musicDir=Path("/media/veracrypt1/music")
ambientDir=Path("/media/veracrypt1/system/ambientMusic")

def addFromM3U():

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

def extRemap(filePath, newExt='.mp3'):
    pre, ext = os.path.splitext(filePath)
    fileRemap = filePath.replace(ext, newExt)

    return fileRemap

def mobilePlaylistSync():
    allPlaylistSongs = []
    allCurrentSongs = []

    # -- Metadata backsync

    # songs = mobileDir.rglob("*.mp3")

    # for songPath in songs:
    #     song = songPath.absolute().as_posix()
    #     allCurrentSongs.append(song)

    #     syncMetadata = eyed3.load(song)
    #     songName = song.replace(mobileDir.absolute().as_posix()+"/","")
    #     #search because we don't know if we did a conversion. sort by size
    #     searchOrigPath = sorted(glob.glob(musicDir.absolute().as_posix()+"/"+songName.replace('.mp3','.*')), key=os.path.getsize)
    #     origPath = ''
    #     origMetadata = None

    #     try:
    #         for p in searchOrigPath:
    #             #todo:load by id3 path here for flac mp3 conv
    #             origMetadata = eyed3.load(Path(searchOrigPath[0]))
    #             if origMetadata != None:
    #                 origPath = Path(searchOrigPath[0])
    #                 break
    #     except Exception as e:
    #         print(e)
    #         continue
        
    #     if origMetadata == None:
    #         continue
    #     origMetadata.tag = syncMetadata.tag
        
    #     if syncMetadata.tag.play_count != None:
    #         print(origMetadata.tag.play_count)
    #     # syncMetadata.save()

    print("")

    for playlist in playlistDir.glob("*.m3u"):
        name = playlist.stem

        match = glob.glob(jellyfinPlaylistDir.absolute().as_posix()+"/"+name+"/playlist.xml")
        if match == []:
            continue

        print(f"Processing Playlist: {name}")

        with open(playlist, 'r') as f:
            songs = f.readlines()

        print(f"Found {len(songs)} songs in the m3u playlist")

        # -- Data

        for song in songs:
            songPath = song.replace("\n","")
            songName = songPath.replace(musicDir.absolute().as_posix()+"/","")

            fullPath = Path(mobileDir.absolute().as_posix()+"/"+songName)
            os.makedirs(fullPath.parent.as_posix(), exist_ok=True)

            if not os.path.exists(songPath):
                print(f"File in playlist, but does not exist on drive:\n{songPath}")
                continue

            if songName.endswith(".mp3"):
                if not os.path.exists(f"{mobileDir.absolute().as_posix()}/{songName}") and os.path.getsize(f"{mobileDir.absolute().as_posix()}/{songName}") == os.path.getsize(f"{songPath}"):
                    # Copy only
                    try:
                        subprocess.run(f'/bin/cp -u "{songPath}" "{mobileDir.absolute().as_posix()}/{songName}"', shell=True, check=True)
                    except subprocess.CalledProcessError as e:
                        print(e)
                        continue
            else:
                songNameOut = extRemap(songName)

                if not os.path.exists(f"{mobileDir.absolute().as_posix()}/{songNameOut}"):
                    # Copy and convert
                    try:
                        # os.symlink(songPath,symlinkDir.absolute().as_posix()+"/"+songName)
                        subprocess.run(f'/usr/bin/ffmpeg -i "{songPath}" -ar 44100 -b:a 320000 -ac 2 -n "{mobileDir.absolute().as_posix()}/{songNameOut}"', shell=True, check=True)
                    except subprocess.CalledProcessError as e:
                        print(e)
                        continue

            allPlaylistSongs.append(f"{mobileDir.absolute().as_posix()}/{songName}")

        # -- Playlist

        syncPlaylist = playlist.absolute().as_posix().replace(playlistDir.absolute().as_posix(), mobileDir.absolute().as_posix())
        with open(syncPlaylist, 'w+') as f:
            for song in songs:
                song = extRemap(song)
                song = song.replace("\n", "")
                songRemap = song.replace(musicDir.absolute().as_posix(), ".") + "\n"

                f.write(songRemap)

    # -- Cleanup

    for song in allCurrentSongs:
        if song not in allPlaylistSongs:
            print(f"Deleting {song} because not found in Playlist songs")
            subprocess.run(f'rm "{song}"')

    def remove_empty_folders(path_abs):
        walk = list(os.walk(path_abs))
        for path, _, _ in walk[::-1]:
            if len(os.listdir(path)) == 0:
                os.rmdir(path)

    remove_empty_folders(mobileDir.absolute().as_posix())

def addFromFolder():
    folders = glob.glob(ambientDir.absolute().as_posix()+"/*")

    for folder in folders:
        name = folder.replace(f"{ambientDir.absolute().as_posix()}/", "")
        match = glob.glob(jellyfinPlaylistDir.absolute().as_posix()+"/"+name+"/playlist.xml")
        if match == []:
            continue

        print(f"Processing Playlist: {name}")

        jellyfinPlaylist = et.parse(match[0])

        jellyfinSongs = list()

        for neighbor in jellyfinPlaylist.iter('Path'):
            jellyfinSongs.append(neighbor.text)

        print(f"Found {len(jellyfinSongs)} songs in the xml playlist")

        songs=glob.glob(f"{folder}/*.mp3")

        print(f"Found {len(songs)} songs in the corresponding ambient music folder")
        
        

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

# jellyfinPlaylistSync()
mobilePlaylistSync()
addFromFolder()