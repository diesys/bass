#!/usr/bin/env python3

import os, sys, json, string, random #, re
from jinja2 import Environment, select_autoescape, FileSystemLoader
from flask import Flask, redirect, send_from_directory, request, flash, url_for #, session 
from colorthief import ColorThief
from requests import get

######## FLASK SERVER APP ##############
app = Flask(__name__, static_url_path="/assets", static_folder='assets')

template_dir = 'assets/templates'
albums_dir = 'albums'
covers_dir = 'covers'
std_id_len = 9
env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=select_autoescape(['html', 'xml'])
)

def getAlbum(album_hash, verbose=False):
    """Album parser"""
    album_path = ''
    for entry in os.listdir(albums_dir):
        if f"_{album_hash}.json" in entry:
            album_filename = entry
            album_path = f"{albums_dir}/{album_filename}"
    
    if (album_path !='') and os.path.exists(album_path):
        f = open(album_path, encoding="utf-8")
        album = json.load(f)
        # check if the image is a web or local url then downloads the image
        if (album['COVER'].split(':')[0] in 'https'):
            f = open(album_path, "w", encoding="utf-8")
            # builds the download path and downloads the img e se non e' jpg??
            download_path = f"{covers_dir}/{album_filename.split('.json')[0]}.jpg"
            download(album['COVER'], download_path)
            # updates the new local url and the file
            album['COVER'] = '/'+download_path
            album['COLOR'] = getMainColor(download_path)
            json.dump(album, f)
            f.close()
        else:
            # removes "/" for relative positioning
            album['COLOR'] = getMainColor(album['COVER'][1:])
        
        if(verbose):
            print(f"Selected album: {album}")
        return album
    return False

## DA FARE MOOOOLTO MEGLIO ((((((((((((((((((((((((((()))))))))))))))))))))))))))
def getList(tracklist=os.listdir(albums_dir), verbose=False):
    """Builds all album list"""
    new_list = {'INFO': {}, 'ITEMS': []}
    for filename in tracklist:
        if filename.endswith('.json'):
            f = open(f"{albums_dir}/{filename}", encoding="utf-8")
            album = json.load(f)
            try:
                if(album['FINDABLE'] != "False"):
                    new_list['ITEMS'].append({
                        'TITLE': album['TITLE'],
                        'COVER': album['COVER'],
                        # sarebbe meglio usare qui url_for nel template? con l'id?
                        'URL': f"a/{filename.split('.')[0].split('_')[-1]}",
                    })
            except KeyError:
                pass

    new_list['INFO']['BACKGROUND'] = '/assets/img/todaybg.jpg'
    if(verbose):
        print(f"All albums: {new_list}")
    return new_list

def todayTheme(verbose=False):
    response = get("https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=it-IT")
    jsonResponse = response.json()
    theme = {'BING_URL': f"https://bing.com{jsonResponse['images'][0]['url']}"}
    download(theme['BING_URL'], 'assets/img/todaybg.jpg')
    theme['COLOR'] = getMainColor('assets/img/todaybg.jpg')
    if(verbose):
        print(f"Today's bing theme is: {theme}")
    return theme

def download(url, file_name, verbose=False):
    """File download"""
    with open(file_name, "wb") as file:
        response = get(url)
        file.write(response.content)
    if(verbose):
        print(f"Downloading: '{url}' to '{file_name}'")

def getMainColor(image_path, verbose=False):
    """Gets predominant image color"""
    color_thief = ColorThief(image_path)
    main_color = f"rgb{color_thief.get_color(quality=100)}"
    # palette = color_thief.get_palette(color_count=2)
    if(verbose):
        print(f"Main color: '{image_path}' is '{main_color}'")
    return main_color

def renderErrPage(error):
    """Error pages template renderer"""
    return env.get_template('error.html').render(ERROR=error,TITLE=error, COLOR=today_theme['COLOR'], BLOCK='error')

def newID(length=std_id_len):
    letters = string.ascii_letters + string.digits
    rand_str = ''.join(random.choice(letters) for i in range(length))

    for entry in os.listdir(albums_dir):
        if f"_{rand_str}.json" in entry:
            newID()
        else:
            return rand_str

def searchAudio(string):
    result = []
    for entry in os.listdir(albums_dir):
        if string in entry:
            result.append(entry)
    return result

## Today bing image and color
today_theme = todayTheme()    

######## ROUTING
@app.route("/")
def home():
    """Homepage"""
    return env.get_template('home.html').render(TITLE="Welcome on BASS", COLOR=today_theme['COLOR'], BLOCK='home')

@app.route("/search", methods=['POST'])
def search():
    """Search page"""
    result_list = getList(searchAudio(request.form['search']))
    title = f"'{request.form['search']}' search result"
    return env.get_template('list.html').render(TITLE=title, COLOR=today_theme['COLOR'], AUTHOR=title, LIST=result_list, BLOCK='list')

@app.route("/add-album")
def addAlbum():
    """Create new album"""
    return env.get_template('add_album.html').render(TITLE="Add album", COLOR=today_theme['COLOR'], BLOCK='add_album', NEW_HASH=newID())

@app.route("/add-tracks", methods=["POST", "GET"])
def addTracks():
    """Add tracks to the new album"""
    album = request.form
    return env.get_template('add_tracks.html').render(TITLE=f"Add tracks to {album['TITLE']}", ALBUM=album, LENGHT=int(album['LENGHT']), COLOR=today_theme['COLOR'], BLOCK='add_tracks')

@app.route("/a/<id>/")
def showAlbum(id):
    """Album by ID page"""
    album = getAlbum(id)
    if album:
        return env.get_template('album.html').render(TITLE=f"{album['TITLE']} ({album['AUTHOR']})", ALBUM=album, BLOCK='album')
    else:
        return renderErrPage("Album not found")

@app.route("/covers/<filename>")
def covers(filename):
    """Serves downloaded covers file image"""
    return send_from_directory(app.root_path + "/covers/", filename)

@app.route("/albums/")
def allAlbums():
    """All albums"""
    all_albums = getList()
    if all_albums:
        return env.get_template('list.html').render(TITLE="All albums", COLOR=today_theme['COLOR'], AUTHOR="All albums", LIST=all_albums, BLOCK='list')
    else:
        return renderErrPage("Something happened while loading albums")
