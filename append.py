import sys
import feedparser
from urllib2 import HTTPError, URLError
import logging

def __fetch_feed(url):
    try:
        feed = feedparser.parse(url)

        return feed.entries[0]
    except HTTPError, e:
        logging.error('Failed with HTTP status code %d' % e.code)
        return None
    except URLError, e:
        logging.error('Failed to connect with network.')
        logging.debug('Network failure reason, %s.' % e.reason)
        return None

def __append_mp3(entry):
    latest = __fetch_feed('cmdln_mp3_in.xml')
    if entry.title.find(latest.title) != -1:
        logging.info('Up to date.')
        return
    f = open('cmdln_mp3_in.xml')
    o = open('cmdln_mp3_out.xml', 'w')
    first = False
    try:
        for line in f:
            if line.find('<item>') != -1 and not first:
                logging.info('Insert new item.')
                first = True
            else:
                logging.info('Preserve existing item.')
            o.write(line)
    finally:
        f.close()

def main():
    logging.basicConfig(level=logging.INFO,
            format='%(message)s')
    entry = __fetch_feed('http://thecommandline.net/category/podcast/feed/')
    if entry is None:
        logging.error('Failed to fetch feed.')
        sys.exit(1)

    __append_mp3(entry)

    print entry.title

if __name__ == "__main__":
    main()
