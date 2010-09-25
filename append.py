#!/usr/bin/python
import sys
import feedparser
import urllib2
from urllib2 import HTTPError, URLError
import logging
import re
from BeautifulSoup import BeautifulSoup
import shutil
import time
import datetime



def __fetch_feed(url):
    try:
        return feedparser.parse(url)
    except HTTPError, e:
        logging.error('Failed with HTTP status code %d' % e.code)
        return None
    except URLError, e:
        logging.error('Failed to connect with network.')
        logging.debug('Network failure reason, %s.' % e.reason)
        return None


def __append(feed, suffix, append_fn):
    latest = __fetch_feed('cmdln_%s.xml' % suffix).entries[0]
    entry = feed.entries[0]
    if latest.title.find(entry.title) != -1:
        logging.info('%s is up to date.' % suffix)
        return

    base_url = 'http://www.archive.org/download/%s' % __archive_slug(entry.title)
    filename = 'cmdln_%s.xml' % suffix
    today = datetime.date.today()
    backup = '%s.%s' % (filename, today.strftime('%Y-%m-%d'))
    shutil.copy(filename, backup)
    f = open(backup)
    o = open(filename, 'w')
    firstItem = False
    try:
        updated = time.strftime('%a, %d %b %Y %X +0000', feed.updated)
        for line in f:
            if line.find('<item>') != -1 and not firstItem:
                append_fn(entry, o, suffix, base_url)
                firstItem = True
            if line.startswith('        <pubDate>'):
                line = '        <pubDate>%s</pubDate>\n' % updated
            if line.startswith('        <lastBuildDate>'):
                line = '        <lastBuildDate>%s</lastBuildDate>\n' % updated
            o.write(line)
    finally:
        f.close()
        o.close()


def __append_non_itunes(entry, output, suffix, base_url):
    (url, mime_type, size) = __enclosure(entry.enclosures, base_url, suffix)
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
    logging.info('Inserted new %s item.' % suffix)


def __append_itunes(entry, output, suffix, base_url):
    description = __description(entry.content)
    soup = BeautifulSoup(description)
    summary = '\n\n'.join([''.join(p.findAll(text=True)) for p in soup.findAll('p')])
    (url, mime_type, size) = __enclosure(entry.enclosures, base_url, suffix)
    if size == 0:
        raise Exception('Couldn not find media, %s.' % base_url)
    output.write("""        <item>
            <title>%(title)s (Comment Line 240-949-2638)</title>
            <link>%(link)s</link>
            <description><![CDATA[%(description)s]]></description>
            <pubDate>%(pubDate)s</pubDate>
            <enclosure url="%(url)s" length="%(size)s" type="%(mime_type)s"/>
            <guid isPermaLink="false">%(permalink)s</guid>
            <itunes:author>Thomas Gideon</itunes:author>
            <itunes:subtitle>%(subtitle)s</itunes:subtitle>
            <itunes:summary>%(summary)s</itunes:summary>
            <itunes:explicit>no</itunes:explicit>
            <itunes:duration>%(duration)s</itunes:duration>
        </item>
""" % { 'title': entry.title,
        'link': entry.link,
        'description': description,
        'pubDate' : entry.date,
        'permalink' : __permalink(entry.title),
        'url' : url,
        'mime_type' : mime_type,
        'size' : size,
        'subtitle' : ''.join(soup.contents[0].findAll(text = True)),
        'summary' : summary,
        'duration' : entry.itunes_duration })
    logging.info('Inserted new %s item.' % suffix)


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


def __archive_slug(title):
    slug = re.sub('\([^0-9]\)-\([^0-9]\)', '\1\2', title)
    slug = re.sub('[^A-Za-z0-9\-]', ' ', slug)
    slug = re.sub(' {2,}', ' ', slug)
    tokens = slug.split(' ')
    tokens = [t.capitalize() for t in tokens]
    slug = ''.join(tokens)
    return slug


def main():
    logging.basicConfig(level=logging.INFO,
            format='%(message)s')
    feed = __fetch_feed('http://thecommandline.net/category/podcast/feed/')
    if feed is None:
        logging.error('Failed to fetch feed.')
        sys.exit(1)

    __append(feed, 'mp3', __append_non_itunes)
    __append(feed, 'ogg', __append_non_itunes)
    __append(feed, 'm4a', __append_itunes)


if __name__ == "__main__":
    
    main()
