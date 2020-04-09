import os
import sys
import webbrowser
from urllib.parse import quote
from urllib.request import urlopen

from flask import Flask, render_template, request
from youtube_dl import YoutubeDL

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)

strURL = "http://127.0.0.1:5000"
webbrowser.open_new(strURL)


def keywordSearch(keyword):
    page = str(urlopen("https://www.youtube.com/results?search_query=" + keyword).read())
    page_source = page.split()

    temp = 0
    link_output = []  # OUTPUT VIDEO LINKS FROM SEARCH

    for element in page_source:
        if element[0:15] == 'href="/watch?v=' and len('www.youtube.com' + element[6:len(element) - 1]) == 35:
            temp += 1
            if temp % 2 == 0 and temp <= 10:
                link_output += ['https://www.youtube.com' + element[6:len(element) - 1]]

    return link_output


def extractMeta(link_out):
    global gen_info
    gen_info = []
    ydl = YoutubeDL()
    ydl.add_default_info_extractors()

    for link in link_out:
        meta = ydl.extract_info(link, download=False)
        for formats in meta['formats']:
            if formats['format_id'] == '18':
                gen_info.append([meta['id'], meta['title'], meta['thumbnail'], formats['url']])


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/', methods=['POST', 'GET'])
def result():
    query = ""
    if request.method == 'POST':
        query = request.form["query"]

    query = quote(query)
    link_out = keywordSearch(query)

    extractMeta(link_out)

    return render_template('result.html', info=gen_info)


@app.route('/YouTube/<video_id>', methods=['GET', 'POST'])
def view_video(video_id):
    if request.method == 'GET':
        for vid, title, thumbnail, url in gen_info:
            if video_id == vid:
                return render_template('video.html', url=url)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown', methods=['POST', 'GET'])
def shutdown():
    shutdown_server()
    return 'Server shut down!'


if __name__ == '__main__':
    app.run()
