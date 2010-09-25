#!/usr/bin/python
from BeautifulSoup import BeautifulStoneSoup
import re
import urllib2
from urllib2 import HTTPError, URLError
import os.path
import logging



def __repoint():
    logging.basicConfig(level=logging.INFO,
            format='%(message)s')
    f = open("cmdln_m4a.xml")
    try:
        soup = BeautifulStoneSoup(f)
        enclosures = soup.findAll('enclosure')
        for enclosure in enclosures:
            url = enclosure['url']
            if url.find('archive.org') != -1:
                continue
            title = enclosure.findPreviousSibling('title')
            rewritten = 'http://www.archive.org/download/%s/%s' % (__archive_slug(title.string),
                os.path.basename(url))
            (mime_type, length) =  __url_info(rewritten)
            if mime_type is None:
                print 'Could not find media, %s.' % rewritten
                break
            enclosure['url'] = rewritten
            enclosure['type'] = mime_type
            enclosure['length'] = length
        print soup
    finally:
        f.close()


def __archive_slug(title):
    paren = title.find('(')
    slug = title[:paren -1]
    slug = re.sub('\([^0-9]\)-\([^0-9]\)', '\1\2', slug)
    slug = re.sub('[^A-Za-z0-9\-]', ' ', slug)
    slug = re.sub(' {2,}', ' ', slug)
    tokens = slug.split(' ')
    tokens = [t.capitalize() for t in tokens]
    slug = ''.join(tokens)
    return slug

def __url_info(url):
    try:
        usock = urllib2.urlopen(url)
        if usock.info() is None:
            return (None, None)
        return (usock.info().type, usock.info().get('Content-Length'))
    except HTTPError, e:
        logging.error('Failed with HTTP status code %d' % e.code)
        return (None, None)
    except URLError, e:
        logging.error('Failed to connect with network.')
        logging.debug('Network failure reason, %s.' % e.reason)
        return (None, None)

if __name__ == "__main__":
    __repoint()
