#!/usr/bin/python
#
# relink.py - A script intended for one time use to tweak a feed to re-link its
# enclosures to appropriate URLs at the Internet Archive.
#
# All project files are made available under the following, BSD-new license.
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
from BeautifulSoup import BeautifulStoneSoup
import re
import urllib2
from urllib2 import HTTPError, URLError
import os.path
import logging
import shutil
import datetime



# TODO this could be re-worked to help re-write one of the existing feeds to produce an initial flac feed
def __repoint():
    """ Iteratest through the feed, re-writing the enclosures. """
    logging.basicConfig(level=logging.INFO,
            format='%(message)s')
    today = datetime.date.today()
    filename = 'cmdln_m4a.xml'
    backup = '%s.%s' % (filename, today.strftime('%Y-%m-%d'))
    shutil.copy(filename, backup)
    f = open(backup)
    o = open(filename, 'w')
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
            (mime_type, length) =  __url_info(rewritten, enclosure['type'], enclosure['length'])
            if mime_type is None:
                print 'Could not find media, %s.' % rewritten
                break
            enclosure['url'] = rewritten
            enclosure['type'] = mime_type
            enclosure['length'] = length
        o.write(str(soup))
    finally:
        f.close()
        o.close()


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

def __url_info(url, mime_type, length):
    try:
        usock = urllib2.urlopen(url)
        if usock.info() is None:
            return (None, None)
        mime_type = usock.info().type
        length = usock.info().get('Content-Length')
        if length is None:
            return (mime_type, None)
        return (mime_type, length)
    except HTTPError, e:
        logging.error('Failed with HTTP status code %d' % e.code)
        return (None, None)
    except URLError, e:
        logging.error('Failed to connect with network.')
        return (None, None)


if __name__ == "__main__":
    __repoint()
