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
function clean {
	if [ -f "$1" ]
	then
		echo "Cleaning existing file, $1."
		rm $1
	fi
}

if [ -z "$1" ]
then
	echo "Provide a cast type!"
	echo "$0 <cast config> <slug> [date]"
	exit 1
fi
config=$1
if [ -z "$2" ]
then
	echo "Provide a slug!"
	echo "$0 <cast config> <slug> [date]"
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

# load info from cast specific config file
. $config

if [ -z "${file_prefix}" ]
then
	echo "${config} must set file_prefix."
	exit 1
fi

echo "Info for tagging."
echo "Title:      $title"
echo "Artist:     $artist"
echo "Cover:      $cover"
echo "Album:      $album"
echo "Genre:      $genre"
echo "URL:        $url"
echo "Copyright:  $copyright"
echo "Comment:    $comment"

base_file=${file_prefix}${date}

echo ""
echo "Encoding MP3, ${base_file}.mp3 at ${mp3_bitrate} kbps."
clean "${base_file}.mp3"
echo ""
# encode lossy, MP3, adding ID3v2 tags for everything
# *except* cover art
lame -b ${mp3_bitrate} \
--cbr \
--tt "${title}" \
--ta "${artist}" \
--tl "${album}" \
--ty "${year}" \
--tc "${comment}" \
--tg "${genre}" \
--id3v2-only \
--noreplaygain \
${base_file}.wav \
${base_file}.mp3

# lame package from Lucid lacks the --ti switch for image
# found eyed3 via a web search
eyeD3 --add-image ${cover}:FRONT_COVER \
--set-text-frame="TCOP:${copyright}" \
${base_file}.mp3

echo ""
echo "Encoding ${base_file}.flac."
clean "${base_file}.flac"
echo ""
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
${base_file}.wav

echo ""
echo "Encoding ${base_file}.m4a at ${aac_quality}."
clean "${base_file}.m4a"
echo ""
# AAC encoding, lossy
# docs recommend against setting bandwidth and bitrate setting
# doesn't seem to result in the desired quality as tweaking
# the quality setting (max 500)--200 was arrived at by iteratively
# encoding the same raw audio and subjective listening to the results
avconv -i ${base_file}.wav \
-b ${aac_quality}k \
-metadata title="${title}"  \
-metadata artist="${artist}" \
-metadata album="${album}" \
-metadata year="${year}"  \
-metadata genre="${genre}" \
-metadata writer="${artist}" \
-metadata comment="${comment}"  \
-strict experimental \
${base_file}.m4a

#-metadata cover-art="${cover}" \
#-acodec fdk_aac \

#faac -q ${aac_quality} \
#-o ${base_file}.m4a \
#--title "${title}"  \
#--artist "${artist}" \
#--album "${album}" \
#--year "${year}" \
#--genre "${genre}" \
#--writer "${artist}" \
#--comment "${comment}"  \
#--cover-art "${cover}" \
#${base_file}.wav

if [ -f ${aac_notes_path}/${date}.notes ]
then
	# put together the just-so input file for mp4chaps
	echo "00:00:00.000 Start" > \
	${base_file}.chapters.txt
	grep "{{offset|" ${aac_notes_path}/${date}.notes | \
	sed -e "s/.*offset|\(.*\)}}.*|\(.*\)}}.*/\1 \2/" >> \
	${base_file}.chapters.txt

	# write the chapter marks to the AAC/MP4 file
	mp4chaps -o -z -i ${base_file}.m4a
fi

echo ""
echo "Encoding ${base_file}.ogg at quality ${ogg_quality}."
clean "${base_file}.ogg"
echo ""
# encode the Ogg Vorbis from the flac copies the tags/comments
# already set into the flac file except the cover art;
# using metaflac, can encode the binary block in flac
# per the latest recommendations from Xiph for cover art
oggenc \
-q ${ogg_quality} \
--comment=METADATA_BLOCK_PICTURE="$(metaflac --export-picture-to=- ${base_file}.flac| base64 -w 0)"  \
${base_file}.flac
