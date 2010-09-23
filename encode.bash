#!/bin/bash
if [ -z "$1" ]
then
	echo "Provide a cast type!"
	exit 1
fi
type=$1
if [ -z "$2" ]
then
	echo "Provide a slug!"
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

title="The Command Line ${date}"
artist="Thomas Gideon"
cover="${HOME}/Dropbox/Public/color_cover_art.jpg"
album="The Command Line"
genre="Podcast"
url="http://thecommandline.net/${post_date}/${slug}/"
copyright="http://creativecommons.org/licenses/by-sa/3.0/us"
comment="Weekly ${type} cast.  Email to feedback@thecommandline.net.  Show notes and license information for this episode at ${url}."

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

faac -q 100 \
-b 96 \
-c 44100 \
-o cmdln.net_${date}.m4a \
--title "${title}"  \
--artist "${artist}" \
--album "${album}" \
--year "${year}" \
--genre "${genre}" \
--writer "${artist}" \
--comment "${comment}"  \
--cover-art ~/Dropbox/Public/color_cover_art.jpg \
cmdln.net_${date}.wav

oggenc \
--comment=METADATA_BLOCK_PICTURE="$(metaflac --export-picture-to=- cmdln.net_${date}.flac| base64 -w 0)"  \
cmdln.net_${date}.flac

lame -b 112 \
--cbr \
--tt "${title}" \
--ta "${artist}" \
--tl "${album}" \
--ty "${year}" \
--tc "${comment}" \
--tg "${genre}" \
--id3v2-only \
cmdln.net_${date}.wav \
cmdln.net_${date}.mp3

