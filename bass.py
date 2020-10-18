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

def getAlbum(album_author, album_name, verbose=False):
    """Album parser"""
    audio_path = f"{albums_dir}/{album_author}/{album_name}.json"
    if os.path.exists(audio_path):
        f = open(audio_path, encoding="utf-8")
        album = json.load(f)
        # check if the image is a web or local url then downloads the image
        if (album['COVER'].split(':')[0] in 'https'):
            f = open(audio_path, "w", encoding="utf-8")
            # builds the download path and downloads the img e se non e' jpg??
            download_path = f"{covers_dir}/{album_author}-{album['TITLE'].replace(' ','_')}.jpg"
            download(album['COVER'], download_path)
            # updates the new local url and the file
            album['COVER'] = '/'+download_path
            album['COLOR'] = 'rgb' + str(getMainColor(download_path))
            json.dump(album, f)
            f.close() #?????????????/
        # else:
        #     album['COLOR'] = 'rgb' + str(getMainColor(album['COVER'][1:]))
        return album
    return False

## DA FARE MOOOOLTO MEGLIO
def getList(author_name="ALL", verbose=False):
    """Builds album list for the given author"""
    list = {'INFO': {}, 'ITEMS': []}
    if author_name == "ALL":
        # if os.path.exists(author_dir):
    # try:
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
        
        # bing image of the day
        response = get("https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=it-IT")
        jsonResponse = response.json()
        list['INFO']['BACKGROUND'] = f"https://bing.com{jsonResponse['images'][0]['url']}"
    # except:
    #     print('aaaa')
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
    return list

# def getAllLists(verbose=False):
#     """See getList"""

def download(url, file_name):
    """File download"""
    with open(file_name, "wb") as file:
        response = get(url)
        file.write(response.content)

def getMainColor(image_path):
    """Gets predominant image color"""
    color_thief = ColorThief(image_path)
    # palette = color_thief.get_palette(color_count=2)
    return color_thief.get_color(quality=100)

######## ROUTING
@app.route("/")
def all(author="ALL"):
    """Homepage All albums"""
    # return url_for(artist("ALL"))
    curr_list = getList(author)
    return env.get_template('list.html').render(TITLE=author, AUTHOR=author, LIST=curr_list, BLOCK='list')

@app.route("/a/<author>/<album>/")
def album(author, album):
    """Album page"""
    curr_album = getAlbum(author, album)
    return env.get_template('album.html').render(TITLE=curr_album['TITLE'], ALBUM=curr_album, BLOCK='album')

@app.route("/a/<author>/")
def list(author):
    """Artist page"""
    curr_list = getList(author)
    return env.get_template('list.html').render(TITLE=author, AUTHOR=author, LIST=curr_list, BLOCK='list')

@app.route("/covers/<filename>")
def covers(filename):
    """Serves downloaded covers file image"""
    return send_from_directory(app.root_path + "/covers/", filename)

# @app.route("/covers/<path:filename>")
