#-*-coding: utf-8 -*-

import base64
import datetime
import glob
import os.path
import PyRSS2Gen
import subprocess
from recipe import compile_recipe

from flask import Flask, request, make_response, redirect
app = Flask(__name__)
app.debug = True

from jinja2 import Template

@app.route('/')
def index():
    return Template('''
<ul>
{% for i in recipes %}
    <li><a href='/gen?recipe={{ i }}'>{{ i }}</li>
{% endfor %}
</ul>
''').render(recipes=[os.path.basename(i).rsplit('.', 1)[0] for i in glob.glob('recipes/*.recipe')])

from flask import request

@app.route('/gen')
def gen():
    fname = os.path.join(os.path.dirname(__file__), 'recipes', request.args.get('recipe'))

    recipe = compile_recipe(open('%s.recipe' % fname).read())
    feeds = recipe(request.args).cook()

    rss = PyRSS2Gen.RSS2(
        title = feeds['title'],
        link = feeds['site_url'],
        description = feeds['description'],
        lastBuildDate = datetime.datetime.now(),
        items = [
           PyRSS2Gen.RSSItem(
               title = i['title'],
               link = i['url'],
               description = i['article'],
               guid = PyRSS2Gen.Guid(i['url']),
               #pubDate = datetime.datetime(2003, 9, 6, 21, 31)
               )
           for i in feeds['articles']
        ])
    resp = make_response(rss.to_xml(encoding='utf-8'))
    resp.headers['content-type'] = 'application/xml'
    return resp

@app.route('/y')
def youtube():
    url = request.args.get('url')
    if url:
        y_url = subprocess.check_output(['youtube-dl', '-g', '-f', 'worstaudio', url]).strip()
        return redirect('/a/%s.html' % base64.b64encode(y_url))
    else:
        return '''
<html>
<head>
<meta name="viewport" content="width=device-width">
<link href="https://cdn.staticfile.org/twitter-bootstrap/4.1.3/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<div class='container'>
<br/><br/></br>
<form action="/y" method="get">
  <div class="form-group"><input type="text" name="url" class="form-control" placeholder="输入 youtube URL"></div>
  <button type="submit" class="btn btn-primary">播放</button>
</form>
</div>
</body>
</html>
'''

@app.route('/a/<path:token>.html')
def audio(token):
    url = base64.b64decode(token)
    return Template('''
<html>
<head>
<meta name="viewport" content="width=device-width">
<script src="https://cdn.staticfile.org/html5media/1.1.8/html5media.min.js"></script>
<style>
.container {
    position: absolute;
    top: 50%;
    left: 50%;
    -moz-transform: translateX(-50%) translateY(-50%);
    -webkit-transform: translateX(-50%) translateY(-50%);
    transform: translateX(-50%) translateY(-50%);
}
</style>
<script type="text/javascript">
function x(speed) {
    document.getElementsByTagName('audio')[0].playbackRate = speed;
}

function sx(t) {
    document.getElementsByTagName('audio')[0].currentTime += t;
}
</script>
</head>
<body style="background-color: black">
<div class='container'>
<audio preload="auto" controls="controls" autoplay>
  <source src="{{url}}"></source>
</audio>
<br/>
<br/>
<div>
<center>
<a href="#" onclick="x(1.0);return false;">1.0</a>&nbsp;&nbsp;
<a href="#" onclick="x(1.25);return false;">1.25</a>&nbsp;&nbsp;
<a href="#" onclick="x(1.5);return false;">1.5</a>&nbsp;&nbsp;
<a href="#" onclick="x(1.75);return false;">1.75</a>&nbsp;&nbsp;
<a href="#" onclick="x(2.0);return false;">2.0</a>&nbsp;&nbsp;
<br/><br/>
<a href="#" onclick="sx(-15);return false;">-15s</a>&nbsp;&nbsp;
<a href="#" onclick="sx(15);return false;">+15s</a>
</center>
</div>
</div>
<script type="text/javascript">
document.getElementsByTagName('audio')[0].playbackRate = 1.5
</script>
</body>
</html>
''').render(url=url)

if __name__ == '__main__':
    app.run(port=5000)
