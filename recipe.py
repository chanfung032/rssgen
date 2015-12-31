import urllib2
from bs4 import BeautifulSoup
from readability.readability import Document

class Recipe(object):

    def index_to_soup(self, url):
        return BeautifulSoup(urllib2.urlopen(url))

    def parse_index(self):
        raise NotImplemented()

    def parse_article(self, url):
        html = urllib2.urlopen(url).read()
        article = Document(html).summary()
        return article

    def url_to_article(self, url):
        return '<a href="%s">%s</a>' % (url, url)

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
