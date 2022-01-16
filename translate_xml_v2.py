#!/usr/bin/env python
#
#

import urllib, httplib
import json
import re
import time
import sys

import xml.etree.ElementTree as ET

from elementtree.ElementTree import parse
from elementtree.ElementTree import Element

from codecs import open

from azure_translator import Translator

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree


class Token(object):
    def __init__(self, client_id, client_secret):
        self.client_id = client_id;
        self.client_secret = client_secret
        self.init = True
        self.token = None

    def getToken(self, re_init=False):
        if not self.init and not re_init:
            if time.time() - self.start_time < 580:
                return self.token
        self.init = False
        self.start_time = time.time()
        params = urllib.urlencode({'client_id': self.client_id, 'client_secret': self.client_secret,
                'scope': "http://api.cognitive.microsoft.com", "grant_type":"client_credentials"})
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

        conn = httplib.HTTPSConnection("api.cognitive.microsoft.com")
        conn.request("POST", "/sts/v1.0", params)
        rs = json.loads ( conn.getresponse().read() )
        self.token = rs[u'access_token']
        return self.token

class BingTranslator(object):
    def __init__(self, client_id, client_secret):
        self.token_obj = Token(client_id, client_secret)

    def unicode2utf8(self, text):
        try:
            if isinstance(text, unicode):
                text = text.encode('utf-8')
        except Exception as (e, msg):
            print e, msg
            pass
        return text

    def getText(self, xml):
        text = re.sub(r"<.+?>", " ", xml).strip()
        return text

    def getTranslation(self, text, src, tgt, reinit_token = False):
        token = self.token_obj.getToken(reinit_token)
        headers = {'Authorization':'bearer %s' % token}
        conn = httplib.HTTPConnection('api.cognitive.microsoft.com')
        dic = {}
        dic['from'] = src
        dic['to'] = tgt
        dic['text'] = self.unicode2utf8(text)
        addr = '/sts/v1.0?' + urllib.urlencode(dic)
        conn.request("GET", addr, headers=headers)
        xml = conn.getresponse().read()
        return self.getText(xml)

if __name__ == "__main__":
    t = Translator('client_secret')

    filename = sys.argv[1] #"input_it.ts"
    language = sys.argv[2]

    parser = etree.XMLParser(encoding="utf-8")
    tree = etree.parse(filename, parser=parser)

    root = tree.getroot()

    print root

	#print(sys.stdout.encoding)
	#print(sys.stdout.isatty())
	#print(locale.getpreferredencoding())
	#print(sys.getfilesystemencoding())
	#print(os.environ["PYTHONIOENCODING"])
	#print(chr(246), chr(9786), chr(9787))

    n = 0
    names = []

    for message in root.iter('message'):
        if n>=0:
            #for elem in messages:
            source_line = message.find('source')
            source = source_line.text

            #message.find('translation').text = translation
            line = message.find("translation")
            #if line.attrib.get('type')=='unfinished':
            #translation = t.translate(source, source_language='it', to='id') #translator.getTranslation (source, "it", language)
            #print "%d %s" % (n, translation)
            #line.text = translation #.decode('utf8')
            #line.set('type', 'finished')
        n=n+1
        names.append(message)

    max = n
    n = 0
    names = []

    for message in root.iter('message'):

        if n>=0:
            #for elem in messages:
            source_line = message.find('source')
            source = source_line.text

            #message.find('translation').text = translation
            line = message.find("translation")
            #if line.attrib.get('type')=='unfinished':
            translation = t.translate(source, source_language='it', to='id')
            #print "%d %s" % (n, translation)
            line.text = translation #.decode('utf8')
            #line.set('type', 'finished')
        n=n+1
        names.append(message)
        progress = n/max
        sys.stdout.write("Translation progress: %d %% (%d of %d)  \r" % (progress, n, max) )
        sys.stdout.flush()

#    writeToFile(names)
    tree.write('output_id.xml', encoding="utf8", xml_declaration=None, default_namespace=None, method="xml")
