import sys
import feedparser
import urllib2
from urllib2 import HTTPError, URLError
import logging
import re

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

def __append(entry, suffix, append_fn):
    latest = __fetch_feed('cmdln_%s.xml' % suffix)
    if entry.title.find(latest.title) != -1:
        logging.info('Up to date.')
        return
    f = open('cmdln_%s.xml' % suffix)
    o = open('cmdln_%s_out.xml' % suffix, 'w')
    first = False
    try:
        for line in f:
            if line.find('<item>') != -1 and not first:
                append_fn(entry, o)
                first = True
            o.write(line)
    finally:
        f.close()


def __append_mp3(entry, output):
    (url, mime_type, size) = __enclosure(entry.enclosures, 'http://cmdln.evenflow.nl/mp3', 'mp3')
    output.write("""        <item>
            <title>%(title)s (Comment Line 240-949-2638)</title>
            <link>%(link)s</link>
            <description><![CDATA[%(description)s]]></description>
            <pubDate>%(pubDate)s</pubDate>
            <enclosure url="%(url)s" length="%(size)s" type="%(mime_type)s"/>
            <guid isPermaLink="false">%(permalink)s</guid>
        </item>
""" % { 'title': entry.title,
        'link': entry.link,
        'description': __description(entry.content),
        'pubDate' : entry.date,
        'permalink' : __permalink(entry.title),
        'url' : url,
        'mime_type' : mime_type,
        'size' : size })
    logging.info('Insert new MP3 item.')


def __permalink(title):
    permalink = title.lower()
    permalink = re.sub('-', '', permalink)
    permalink = re.sub('[^a-z0-9]', '-', permalink)
    permalink = re.sub('-{2,}', '-', permalink)
    if len(permalink) > 48:
        permalink = permalink[:48]
    return permalink


def __description(content):
    description = content[0].value
    description = re.sub('<p></p>\n', '', description)
    description = re.sub(re.compile('License</a>.</p>.*$', re.M | re.S), 'License</a>.</p>', description)
    description = re.sub('</p>\n', '</p>\n\n', description)
    return re.sub('<p>View the <a', '<p>More news, commentary, and alternate feeds available at http://thecommandline.net/.  View the <a', description)


def __enclosure(enclosures, base_url, suffix):
    m = re.search('cmdln.net_[0-9]{4}-[0-9]{2}-[0-9]{2}', enclosures[0].href)
    url = '%s/%s.%s' % (base_url, m.group(), suffix)
    usock = urllib2.urlopen(url)
    mime_type = usock.info().type
    size =  usock.info().get('Content-Length')
    if size is None:
        size = 0
    return (url, mime_type, size)


def main():
    logging.basicConfig(level=logging.INFO,
            format='%(message)s')
    #entry = __fetch_feed('http://thecommandline.net/category/podcast/feed/')
    entry = __fetch_feed('cmdln_site.xml')
    if entry is None:
        logging.error('Failed to fetch feed.')
        sys.exit(1)

    __append(entry, 'mp3', __append_mp3)


if __name__ == "__main__":
    
    main()
