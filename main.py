import base64
import datetime
import glob
import os.path
import PyRSS2Gen

from recipe import compile_recipe

from flask import Flask, request, make_response
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

@app.route('/a/<token>.html')
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
</head>
<body style="background-color: black">
<div class='container'>
<audio src="{{url}}" controls preload></audio>
</div>
</body>
</html>
''').render(url=url)

if __name__ == '__main__':
    app.run(port=5000)
