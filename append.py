#!/usr/bin/python
#
# append.py - Compares the podcast category feed for the podcast's web site
# with format specific feeds, adding the newest episode if missing.
#
# Copyright (c) 2010, Thomas Gideon
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Thomas Gideon nor the
#       names of additional contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
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
    """ Pull the feed and parse it, logging any errors. """
    try:
        return feedparser.parse(url)
    except HTTPError, e:
        logging.error('Failed with HTTP status code %d' % e.code)
        return None
    except URLError, e:
        logging.error('Failed to connect with network.')
        logging.debug('Network failure reason, %s.' % e.reason)
        return None


def __append(config, feed, suffix, append_fn):
    """
        For the given main site feed, load the appropriate media specific feed
        and compare.  If the latest episode isn't in the media specific feed,
        insert it making the necessary adjustments to the new episode's entry.
    """
    local_file = '%s%s.xml' % (config['file_prefix'], suffix)
    latest = __fetch_feed(local_file).entries[0]
    entry = feed.entries[0]
    if latest.title.find(entry.title) != -1:
        logging.info('%s is up to date.' % suffix)
        return

    base_url = 'http://www.archive.org/download/%s' % __archive_slug(entry.title)
    filename = '%s%s.xml' % (config['file_prefix'], suffix)
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
                append_fn(config, entry, o, suffix, base_url)
                firstItem = True
            if line.startswith('        <pubDate>'):
                line = '        <pubDate>%s</pubDate>\n' % updated
            if line.startswith('        <lastBuildDate>'):
                line = '        <lastBuildDate>%s</lastBuildDate>\n' % updated
            o.write(line)
    finally:
        f.close()
        o.close()


def __append_non_itunes(config, entry, output, suffix, base_url):
    """ 
        For most of the feeds, new episodes are simple stanzas and the
        adjustments consist mostly of copying what is in the mean site feed's
        entry and just re-writing the enclosure to the appropriate media file.
    """
    (url, mime_type, size) = __enclosure(config, entry.enclosures, base_url, suffix)
    output.write("""        <item>
            <title>%(title)s%(title_suffix)s</title>
            <link>%(link)s</link>
            <description><![CDATA[%(description)s]]></description>
            <pubDate>%(pubDate)s</pubDate>
            <enclosure url="%(url)s" length="%(size)s" type="%(mime_type)s"/>
            <guid isPermaLink="false">%(permalink)s</guid>
        </item>
""" % { 'title': __title(entry.title),
        'link': entry.link,
        'description': __description(config, entry.content),
        'pubDate' : entry.date,
        'permalink' : __permalink(entry.title),
        'url' : url,
        'mime_type' : mime_type,
        'size' : size,
        'title_suffix': config['title_suffix'] })
    logging.info('Inserted new %s item.' % suffix)


def __append_itunes(config, entry, output, suffix, base_url):
    """
        For the iTunes/AAC feed, there are some additional elements that make
        use of the Apple extensions to RSS.  Some of these, like the duration,
        author and subtitle, can be copied as is.  The description and summary
        produced by PodPress is less than desirable so those get munged to
        something more suitable before writing into the iTunes feed.
    """
    description = __description(config, entry.content)
    soup = BeautifulSoup(description)
    summary = '\n\n'.join([''.join(p.findAll(text=True)) for p in soup.findAll('p')])
    if len(summary) > 4000:
        summary = summary[:4000]
    (url, mime_type, size) = __enclosure(config, entry.enclosures, base_url, suffix)
    if size == 0:
        raise Exception('Couldn not find media, %s.' % (url))
    output.write("""        <item>
            <title>%(title)s%(title_suffix)s</title>
            <link>%(link)s</link>
            <description><![CDATA[%(description)s]]></description>
            <pubDate>%(pubDate)s</pubDate>
            <enclosure url="%(url)s" length="%(size)s" type="%(mime_type)s"/>
            <guid isPermaLink="false">%(permalink)s</guid>
            <itunes:author>%(author)s</itunes:author>
            <itunes:subtitle>%(subtitle)s</itunes:subtitle>
            <itunes:summary>%(summary)s</itunes:summary>
            <itunes:explicit>no</itunes:explicit>
            <itunes:duration>%(duration)s</itunes:duration>
        </item>
""" % { 'title': __title(entry.title),
        'link': entry.link,
        'description': description,
        'pubDate' : entry.date,
        'permalink' : __permalink(entry.title),
        'url' : url,
        'mime_type' : mime_type,
        'size' : size,
        'subtitle' : ''.join(soup.contents[0].findAll(text = True)),
        'summary' : summary,
        'duration' : '0:00',
        'title_suffix': config['title_suffix'],
        'author': config['author'] })
    logging.info('Inserted new %s item.' % suffix)


def __permalink(title):
    """ 
        PodPress uses the opaque permalink from WordPress, basically just a
        base url with a minimal query string containing the post's internal ID.
        The OS X app used to maintain these feeds previously, Feeder, munged
        the title into a nice, readable slug.  This function reproduces what
        Feed does to populate the permalink element in the feed entry.
    """
    permalink = title.lower()
    permalink = re.sub('-', '', permalink)
    permalink = re.sub('[^a-z0-9]', '-', permalink)
    permalink = re.sub('-{2,}', '-', permalink)
    if len(permalink) > 48:
        permalink = permalink[:48]
    return permalink


def __title(title):
    fixed = title
    fixed = re.sub(u'\u2013', '-', fixed)
    fixed = re.sub(u'\u201c', '"', fixed)
    fixed = re.sub(u'\u201d', '"', fixed)
    fixed = re.sub(u'\u2019', '\'', fixed)
    fixed = re.sub(u'\xd7', 'x', fixed)
    return fixed


def __description(config, content):
    """ 
        This function strips out parts of the description used in the main site
        feed that are less appropriate for the media specific feeds.  PodPress
        leaves a blank paragraph where its Flash player renders.  The main
        site's episodes have some extra verbiage after the license image and
        links, namely the sharing and relate posts plugin output.  A simple,
        bare link is added to the last paragraph for the benefit of aggregators
        that may strip out HTML.
    """
    description = re.sub(u'\xa0', ' ', content[0].value)
    description = re.sub('<p></p>\n', '', description)
    description = re.sub(re.compile('License</a>.</p>.*$', re.M | re.S), 'License</a>.</p>', description)
    description = re.sub('</p>\n', '</p>\n\n', description)
    description = re.sub(u'\xd7', 'x', description)
    return re.sub('<p>%(info_lede)s' % config, '<p>%(more_info)s  %(info_lede)s' % config, description)


def __enclosure(config, enclosures, base_url, suffix):
    """ 
        Uses the file name from the main site's enclosure plus the base_url to
        pull together values to re-write the attributes for the correct media.
    """
    m = re.search('%s[0-9]{4}-[0-9]{2}-[0-9]{2}' % config['enclosure_prefix'], enclosures[0].href)
    url = '%s/%s.%s' % (base_url, m.group(), suffix)
    usock = urllib2.urlopen(url)
    # Google listen won't play 'application/ogg' and that mime type is currently
    # returned by archive.org for Ogg Vorbis files
    if 'ogg' == suffix:
        mime_type = 'audio/ogg'
    elif 'm4a' == suffix:
        mime_type = 'audio/mp4'
    else:
        mime_type = usock.info().type
    size =  usock.info().get('Content-Length')
    if size is None:
        size = 0
    return (url, mime_type, size)


def __archive_slug(title):
    """ 
        The Internet Archive transforms the title field of new entries in a
        specific way.  This is my reverse engineering of their algorithm based
        on their description and empirical data from dozens of uploads.
    """
    if identifier is not None:
        return identifier
    slug = re.sub('\([^0-9]\)-\([^0-9]\)', '\1\2', title)
    slug = re.sub(u'\u2013', '-', slug)
    slug = re.sub(u'\xd7', 'x', slug)
    slug = re.sub(u'\u2019', '', slug)
    slug = re.sub('[^A-Za-z0-9\-\.(]', ' ', slug)
    slug = re.sub(' {2,}', ' ', slug)
    tokens = slug.split(' ')
    tokens = [__paren_capitalize(t) for t in tokens]
    slug = ''.join(tokens)
    return slug


def __paren_capitalize(token):
    if token.startswith('('):
        token = token[1:]
        return token.lower()
    return token.capitalize()


def __main(feed_file):
    logging.basicConfig(level=logging.INFO,
            format='%(message)s')
    f = open(feed_file)
    config = dict()
    try:
        for line in f:
            if line.startswith('#'):
                continue
            if len(line.strip()) == 0:
                continue
            (name, value) = line.split('=')
            config[name] = value.rstrip()
    finally:
        f.close()
    # pulls the category feed from the web site which will have just the most recent episodes
    # along with all the iTunes jiggery-pokery PodPress performs
    feed = __fetch_feed(config['url'])
    if feed is None:
        logging.error('Failed to fetch feed.')
        sys.exit(1)

    __append(config, feed, 'mp3', __append_non_itunes)
    __append(config, feed, 'ogg', __append_non_itunes)
    __append(config, feed, 'm4a', __append_itunes)
    # TODO add flac


identifier = None

if __name__ == "__main__":
    
    if len(sys.argv) > 2:
        identifier = sys.argv[2]
    __main(sys.argv[1])
