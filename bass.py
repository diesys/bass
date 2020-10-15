#!/usr/bin/env python3

# from __future__ import (print_function, absolute_import, division, unicode_literals)
# from builtins import (filter, open, str)
# from future import standard_library
# standard_library.install_aliases()
## up py3 compatibility => pip install future, below is valid py3
import re, os, sys, json
from jinja2 import Environment, select_autoescape, FileSystemLoader
from flask import Flask, redirect, send_from_directory, request, flash, url_for #, session 
# from flask_login import login_user, current_user, logout_user, login_required
# import telegram

######## FLASK SERVER APP ##############
app = Flask(__name__, static_url_path="/assets", static_folder='assets')
# if __name__ == '__main__':
    # app.run(host='127.0.0.1', port=5000)
    # app.run(host='192.168.1.9', port=5000)

template_dir = 'assets/templates'
audio_dir = 'audio'
env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=select_autoescape(['html', 'xml'])
)
#####################################################################################

def getAlbum(album_author, album_name, verbose=False):
    """Album parser"""
    audio_path = f"{audio_dir}/{album_author}/{album_name}.json"
    if os.path.exists(audio_path):
        f = open(audio_path, encoding="utf-8")
        album = json.load(f)
        return album
    return False

def getList(author, verbose=False):
    """Builds album list for the given author"""

    list = {'INFO':{}, 'ITEMS': []}
    author_dir = f"{audio_dir}/{author}"
    if os.path.exists(author_dir):
        for filename in os.listdir(author_dir):
            if filename.endswith('.json'):
                f = open(f"{author_dir}/{filename}", encoding="utf-8")
                album = json.load(f)
                list['ITEMS'].append({
                    'TITLE': album['TITLE'],
                    'COVER': album['COVER'],
                    # 'URL': f"{author}/{filename.split('.')[0]}",
                    'URL': f"{filename.split('.')[0]}",
                    })
        list['INFO']['BACKGROUND'] = list['ITEMS'][0]['COVER']
    return list

######## HOMEPAGE
# @app.route("/")
# def home():
#     """Homepage"""

#     # return send_from_directory(f"{app.root_path}/{template_dir}", "index.html")
#     return env.get_template('album.html').render(ALBUM=getAlbum(album), BLOCK='album')

@app.route("/a/<author>/<album>/")
def album(author, album):
    """Album page"""
    curr_album = getAlbum(author, album)
    return env.get_template('album.html').render(TITLE=curr_album['TITLE'], ALBUM=curr_album, BLOCK='album')

@app.route("/a/<author>/")
def artist(author):
    """Artist page"""
    curr_list = getList(author)
    return env.get_template('list.html').render(TITLE=author, AUTHOR=author, LIST=curr_list, BLOCK='list')

# @app.route("/m/<path:filename>")
# def staticMenuFiles(filename):
#     """Serves static files needed for the menu index"""
#     return send_from_directory(app.root_path + "/m/", filename)
