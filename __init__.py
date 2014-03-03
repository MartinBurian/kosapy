__author__ = 'martinjr'
__all__ = ["Kosapy"]

import xml.sax
import requests
import requests_cache
import re
from datetime import datetime, date

HEADERS={"content-type": "applicaion/xml;encoding=utf-8",
         "accept-language": "cs"}

requests_cache.install_cache('kosapy_cache', expire_after=24*60*60)

class Kosapy:
    def __init__(self, url, auth, verbose=False):
        self._kosapi=url
        self._auth=auth
        self._verbose=verbose
        self._resources={}

    def __getattr__(self, item):
        if item not in self._resources:
            self._resources[item]=Resource(item, self)

        return self._resources[item]

    def get_feed(self, location, params={}):
        if self._verbose:
            print("Fetching "+self._kosapi+location)
            
        r=requests.get(self._kosapi+location, auth=self._auth, params=params, headers=HEADERS)
        r.encoding='utf-8'
        if r.status_code!=200:
            if r.status_code==403:
                raise Exception('Wrong authentication')
            elif r.status_code==404:
                raise Exception('Resource %s not found'%location)
            elif r.status_code>=500:
                raise Exception('Internal error')
            else:
                raise Exception('Error %d requesting %s'%(r.status_code, location))

        return ObjectiveKosapiDoc(bytes(r.text, 'utf-8'), self)

    def get_contents(self, feed):
        feed=(feed.get("atom:feed") if feed.get("atom:feed") else feed).get("atom:entry")

        if not feed:
            return ()

        for e in feed:
            c=e.get("atom:content")
            selff=e.get("atom:link", rel="self")
            if selff:
                href=selff("href")
                if href[-1]=="/":
                    href=href[:-1]

                c.resource=Resource(href, self)
        return (e.get("atom:content") for e in feed) if feed else ()

    def use_cache(self, use):
        if use:
            requests_cache.install_cache('kosapy_cache', expire_after=24*60*60)
        else:
            requests_cache.uninstall_cache()



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

    def __repr__(self):
        return "<KosAPI resource "+self._location+">"


class ObjectiveKosapiDoc:
    def __init__(self, doc, api):
        self._api=api
        self._root=KosapiElement("root", (), api)
        if doc:
            self._parse_doc(doc)

    def __getattr__(self, item):
        return self._root.__getattr__(item)

    def __call__(self, *args, **kwargs):
        return self._root.__call__(*args, **kwargs)

    def get(self, item):
        return self.__getattr__(item)

    def _parse_doc(self, doc):
        xml.sax.parseString(doc, KosapiSaxHandler(self._root, self._api))


class KosapiElement:
    _redatetime=re.compile("^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")
    _redate=re.compile("^\d{4}-\d{2}-\d{2}$")
    _rebool=re.compile("^true$|^false$")
    _redigit=re.compile("^\d+$")

    def __init__(self, name, attrs, api):
        self._content=""
        self._content_parsed=""
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
            return ()

    def __call__(self, attr="", raw=False):
        if not attr:
            if not self._content_parsed:
                self._parse_content()
            return self._content if raw else self._content_parsed
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

    def __repr__(self):
        return "<KosAPI entry "+self._name+">"

    def _parse_content(self):
        if self._redigit.match(self._content):
            self._content_parsed=int(self._content)
        elif self._redatetime.match(self._content):
            self._content_parsed=datetime.strptime(self._content, "%Y-%m-%dT%H:%M:%S")
        elif self._redate.match(self._content):
            self._content_parsed=datetime.strptime(self._content, "%Y-%m-%d").date()
        elif self._rebool.match(self._content):
            self._content_parsed=self._content.lower()=="true"
        else:
            self._content_parsed=self._content

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


class KosapiSaxHandler(xml.sax.ContentHandler):
    def __init__(self, root, api):
        self.path=[root]
        self._api=api

    def startElement(self, name, attrs):
        element=KosapiElement(name, attrs, self._api)
        self.path[-1].add_element(element)
        self.path.append(element)

    def endElement(self, name):
        self.path.pop()

    def characters(self, content):
        self.path[-1]._content+=content.strip()
