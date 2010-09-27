#!/bin/bash
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
faac -q 100 \
-b 112 \
-c 44100 \
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
-q 4 \
--comment=METADATA_BLOCK_PICTURE="$(metaflac --export-picture-to=- cmdln.net_${date}.flac| base64 -w 0)"  \
cmdln.net_${date}.flac

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
