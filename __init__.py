__author__ = 'martinjr'

import xml.sax
import requests
import requests_cache
import requests_oauthlib as reqo

HEADERS={"content-type": "applicaion/xml;encoding=utf-8"}

requests_cache.install_cache('kosapy_cache', expire_after=24*60*60)

class Kosapy:
    def __init__(self, url, auth):
        self._kosapi=url
        self._auth=auth

        self._resources={}

    def __getattr__(self, item):
        if item not in self._resources:
            self._resources[item]=Resource(item, self)

        return self._resources[item]

    def get_feed(self, location, params={}):
        print("Fetching "+self._kosapi+location)
        r=requests.get(self._kosapi+location, auth=self._auth, params=params, headers=HEADERS)
        r.encoding='utf-8'
        return ObjectiveKosapiDoc(bytes(r.text, 'utf-8'), self)

    def get_contents(self, feed):
        feed=(feed.get("atom:feed") if feed.get("atom:feed") else feed).get("atom:entry")
        return (e.get("atom:content") for e in feed) if feed else ()

class Resource:
    def __init__(self, location, api):
        self._location=location
        self._params={}
        self._children={}

        self._api=api

        self._content=None

    def __call__(self, **kwargs):
        if kwargs:
            self._params=kwargs
            return self
        else:
            if not self._content:
                self._content=self._api.get_contents(self._api.get_feed(self._location, self._params)).__next__()
            return self._content

    def __iter__(self):
        feed=self._api.get_feed(self._location, self._params)
        while True:
            for entry in self._api.get_contents(feed):
                yield entry

            if feed.get("atom:feed") and feed.get("atom:feed").get("atom:link", rel="next"):
                feed=self._api.get_feed(feed.get("atom:feed").get("atom:link", rel="next")("href"))
            else:
                break

    def get(self, item):
        return self.__getattr__(item)


    def __getattr__(self, item):
        if item not in self._children:
            self._children[item]=Resource(self._location+"/"+item, self._api)

        return self._children[item]

class ObjectiveKosapiDoc:
    def __init__(self, doc, api):
        self._api=api
        self._root=Element("root", (), api)
        if doc:
            self._parse_doc(doc)

    def __getattr__(self, item):
        return self._root.__getattr__(item)

    def __call__(self, *args, **kwargs):
        return self._root.__call__(*args, **kwargs)

    def get(self, item):
        return self.__getattr__(item)

    def _parse_doc(self, doc):
        xml.sax.parseString(doc, SaxHandler(self._root, self._api))

class Element:
    def __init__(self, name, attrs, api):
        self._content=""
        self._name=name
        self._attrs=attrs

        self._children={}
        self._ref=None
        self._api=api

    def __getattr__(self, item):
        if "xlink:href" in self._attrs:
            if not self._ref:
                self._ref=Resource(self._attrs.getValue("xlink:href"), self._api)
            return self._ref().get(item)

        if item in self._children:
            return self._children[item]
        else:
            return False

    def __call__(self, attr=""):
        if not attr:
            return self._content
        elif attr in self._attrs:
            return self._attrs.getValue(attr)
        else:
            return False

    def __iter__(self):
        yield self

    def get(self, item, **kwargs):
        if kwargs and item in self._children:
            for el in self._children[item]:
                for attr, value in kwargs.items():
                    if el(attr)==value:
                        return el

        else:
            return self.__getattr__(item)

    def add_element(self, element):
        if element._name in self._children:
            if isinstance(self._children[element._name], list):
                self._children[element._name].append(element)
            else:
                self._children[element._name]=[self._children[element._name], element]
        else:
            self._children[element._name]=element

    def traverse(self):
        if self._children:
            print(self._name)
            for name, child in self._children.items():
                for sub in child:
                    sub.traverse()
        else:
            print("%s: %s (%s)"%(self._name, self._content, str(self._attrs.getNames())))

class SaxHandler(xml.sax.ContentHandler):
    def __init__(self, root, api):
        self.path=[root]
        self._api=api

    def startElement(self, name, attrs):
        element=Element(name, attrs, self._api)
        self.path[-1].add_element(element)
        self.path.append(element)

    def endElement(self, name):
        self.path.pop()

    def characters(self, content):
        self.path[-1]._content+=content.strip()
