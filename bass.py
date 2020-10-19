#!/usr/bin/env python3

import re, os, sys, json
from jinja2 import Environment, select_autoescape, FileSystemLoader
from flask import Flask, redirect, send_from_directory, request, flash, url_for #, session 
from colorthief import ColorThief
from requests import get

######## FLASK SERVER APP ##############
app = Flask(__name__, static_url_path="/assets", static_folder='assets')
# if __name__ == '__main__':
    # app.run(host='192.168.1.9', port=5000) #scoglitti
    # app.run(host='192.168.1.137', port=5000) #comiso

template_dir = 'assets/templates'
albums_dir = 'albums'
covers_dir = 'covers'
env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=select_autoescape(['html', 'xml'])
)
#####################################################################################

# def getAlbum(album_author, album_name, verbose=False):
def getAlbum(album_hash, verbose=False):
    """Album parser"""
    album_path = ''
    for entry in os.listdir(albums_dir):
        if album_hash in entry:
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

## DA FARE MOOOOLTO MEGLIO
def getList(author_name="all", verbose=False):
    """Builds album list for the given author"""
    list = {'INFO': {}, 'ITEMS': []}
    if author_name == "all":
        for author in os.listdir(albums_dir):
            author_dir = f"{albums_dir}/{author}"
            for filename in os.listdir(author_dir):
                if filename.endswith('.json'):
                    f = open(f"{author_dir}/{filename}", encoding="utf-8")
                    album = json.load(f)
                    list['ITEMS'].append({
                        'TITLE': album['TITLE'],
                        'COVER': album['COVER'],
                        'URL': f"a/{author}/{filename.split('.')[0]}",
                    })
        
        list['INFO']['BACKGROUND'] = today_theme['BING_URL']
    else:
        author_dir = f"{albums_dir}/{author_name}"
        if os.path.exists(author_dir):
            for filename in os.listdir(author_dir):
                if filename.endswith('.json'):
                    f = open(f"{author_dir}/{filename}", encoding="utf-8")
                    album = json.load(f)
                    list['ITEMS'].append({
                        'TITLE': album['TITLE'],
                        'COVER': album['COVER'],
                        'COLOR': album['COLOR'],
                        'URL': f"{filename.split('.')[0]}",
                    })
            list['INFO']['BACKGROUND'] = list['ITEMS'][-1]['COVER']
            list['INFO']['COLOR'] = list['ITEMS'][-1]['COLOR']
            print(list['ITEMS'][-1])
    if(verbose):
        print(f"Selected list: {list}")
    return list

def getListAll(verbose=False):
    """Builds all album list"""
    list = {'INFO': {}, 'ITEMS': []}
    for filename in os.listdir(albums_dir):
        if filename.endswith('.json'):
            f = open(f"{albums_dir}/{filename}", encoding="utf-8")
            album = json.load(f)
            list['ITEMS'].append({
                'TITLE': album['TITLE'],
                'COVER': album['COVER'],
                # sarebbe meglio usare qui url_for nel template? con l'id?
                'URL': f"a/{filename.split('.')[0].split('_')[-1]}",
            })
    list['INFO']['BACKGROUND'] = '/assets/img/todaybg.jpg'
    if(verbose):
        print(f"All albums: {list}")
    return list

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


## Today bing image and color
today_theme = todayTheme()    

######## ROUTING
@app.route("/")
def home():
    """Homepage"""
    return env.get_template('home.html').render(TITLE="Welcome on BASS", COLOR=today_theme['COLOR'], BLOCK='home')

@app.route("/a/<id>/")
def showAlbum(id):
    """Album by ID page"""
    album = getAlbum(id)
    if album:
        return env.get_template('album.html').render(TITLE=f"{album['TITLE']} ({album['AUTHOR']})", ALBUM=album, BLOCK='album')
    else:
        return "Error, album not found"

@app.route("/covers/<filename>")
def covers(filename):
    """Serves downloaded covers file image"""
    return send_from_directory(app.root_path + "/covers/", filename)

@app.route("/albums/")
def allAlbums():
    """All albums"""
    curr_list = getListAll()
    return env.get_template('list.html').render(TITLE="All albums", COLOR=today_theme['COLOR'], AUTHOR="All albums", LIST=curr_list, BLOCK='list')
