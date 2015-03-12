__author__ = 'namhyun'
from urlparse import urlparse

class urlbuilder():
    BASE_URL = []

    def __init__(self, base_url):
        self.BASE_URL = []
        self.BASE_URL.append(base_url)

    def append_path(self, path):
        if len(self.BASE_URL) != 0:
            self.BASE_URL.append('/' + path)
        return self

    def append_query_param(self, key, value):
        url_parsed = urlparse(self.build())
        if len(self.BASE_URL) != 0:
            if url_parsed.query is '':
                self.BASE_URL.append("?")
                self.BASE_URL.append(key + "=" + value)
            else:
                self.BASE_URL.append("&")
                self.BASE_URL.append(key + "=" + value)
        return self

    def build(self):
        return ''.join(self.BASE_URL)