import urllib2
import base64
from bs4 import BeautifulSoup
from readability.readability import Document

class Recipe(object):
    ua = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-en) AppleWebKit/533.19.4 (KHTML, like Gecko) Version/5.0.3 Safari/533.19.4'

    def __init__(self, args):
        self.args = args

    def index_to_soup(self, url):
        return BeautifulSoup(urllib2.urlopen(urllib2.Request(url, headers={'User-Agent': self.ua})))

    def parse_index(self):
        raise NotImplemented()

    def parse_article(self, url):
        html = urllib2.urlopen(urllib2.Request(url, headers={'User-Agent': self.ua})).read()
        article = Document(html).summary()
        return article

    def url_to_article(self, url):
        return '<a href="%s">%s</a>' % (url, url)

    def redirect_audio_url(self, url):
        from flask import request
        return 'http://%s/a/%s.html' % (request.headers.get('host'), base64.b64encode(url))

    def cook(self):
        index = self.parse_index()
        for item in index:
            # TODO: add cache
            item['article'] = self.parse_article(item['url'])
        return {'title': self.title,
                'description': self.description,
                'site_url': self.site_url,
                'articles': index}

def compile_recipe(src):
    namespace = {}
    exec src in namespace
    for x in namespace.itervalues():
        if isinstance(x, type) and issubclass(x, Recipe) and x != Recipe: 
            return x
