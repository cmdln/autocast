#!/bin/bash
# 
# encode.bash - Drives a set of encoders and tagging utilities to convert a
# single WAV input file into flac, Ogg Vorbis, AAC and MP3 files with complete
# and consistent metadata.
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
if [ -z "$1" ]
then
	echo "Provide a cast type!"
	echo "$0 <cast type> <slug> [date]"
	exit 1
fi
type=$1
if [ -z "$2" ]
then
	echo "Provide a slug!"
	echo "$0 <cast type> <slug> [date]"
	exit 2
fi
slug=$2
if [ -z "$3" ]
then
	date=$(date +%Y-%m-%d)
	year=$(date +%Y)
	post_date=$(date +%Y/%m/%d)
else
	date=$(date +%Y-%m-%d -d $3)
	year=$(date +%Y -d $3)
	post_date=$(date +%Y/%m/%d -d $3)
fi
echo $date

# assemble common values for tags/comments
title="The Command Line ${date}"
artist="Thomas Gideon"
cover="${HOME}/Dropbox/Public/color_cover_art.jpg"
album="The Command Line"
genre="Podcast"
url="http://thecommandline.net/${post_date}/${slug}/"
copyright="http://creativecommons.org/licenses/by-sa/3.0/us"
comment="Weekly ${type} cast.  Email to feedback@thecommandline.net.  Show notes and license information for this episode at ${url}."

# encode lossy, MP3, adding ID3v2 tags for everything
# *except* cover art
lame -b 112 \
--cbr \
--tt "${title}" \
--ta "${artist}" \
--tl "${album}" \
--ty "${year}" \
--tc "${comment}" \
--tg "${genre}" \
--id3v2-only \
--noreplaygain \
cmdln.net_${date}.wav \
cmdln.net_${date}.mp3

# lame package from Lucid lacks the --ti switch for image
# found eyed3 via a web search
eyeD3 --add-image ${cover}:FRONT_COVER \
--set-text-frame="TCOP:${copyright}" \
cmdln.net_${date}.mp3

# lossless encoding
flac \
--picture="|image/jpeg|||${cover}" \
--tag=title="${title}" \
--tag=artist="${artist}" \
--tag=album="${album}" \
--tag=year="${year}" \
--tag=genre="${genre}" \
--tag=composer="${artist}" \
--tag=comment="${comment}"  \
--tag=url="${url}"  \
--tag=copyright="${copyright}"  \
cmdln.net_${date}.wav

# AAC encoding, lossy
# docs recommend against setting bandwidth and bitrate setting
# doesn't seem to result in the desired quality as tweaking
# the quality setting (max 500)--200 was arrived at by iteratively
# encoding the same raw audio and subjective listening to the results
faac -q 200 \
-o cmdln.net_${date}.m4a \
--title "${title}"  \
--artist "${artist}" \
--album "${album}" \
--year "${year}" \
--genre "${genre}" \
--writer "${artist}" \
--comment "${comment}"  \
--cover-art "${cover}" \
cmdln.net_${date}.wav

# put together the just-so input file for mp4chaps
echo "00:00:00.000 Start" > \
cmdln.net_${date}.chapters.txt
grep "{{offset|" ~/Documents/cmdln_notes/weekly_archive/${date}.notes | \
sed -e "s/.*offset|\(.*\)}}.*|\(.*\)}}.*/\1 \2/" >> \
cmdln.net_${date}.chapters.txt

# write the chapter marks to the AAC/MP4 file
mp4chaps -o -z -i cmdln.net_${date}.m4a

# encode the Ogg Vorbis from the flac copies the tags/comments
# already set into the flac file except the cover art;
# using metaflac, can encode the binary block in flac
# per the latest recommendations from Xiph for cover art
oggenc \
-q 5 \
--comment=METADATA_BLOCK_PICTURE="$(metaflac --export-picture-to=- cmdln.net_${date}.flac| base64 -w 0)"  \
cmdln.net_${date}.flac
