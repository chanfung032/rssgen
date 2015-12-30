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

@app.route('/gen')
def gen():
    fname = os.path.join(os.path.dirname(__file__), 'recipes', request.args.get('recipe'))

    recipe = compile_recipe(open('%s.recipe' % fname).read())
    feeds = recipe().cook()

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

if __name__ == '__main__':
    app.run(port=5000)
