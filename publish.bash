#!/bin/bash

# TODO can upload to archive.org be automated with curl?

# if the other scripts didn't twig you to it, this one reveals my current
# dependence on Dropbox
cp *.xml ~/Dropbox/Public/

# TODO clean out backups older than so many days

# clean out all but the flac files
rm *.wav *.ogg *.aac *.mp3
