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
faac -q 100 \
-b 96 \
-c 44100 \
-o cmdln.net_${date}.m4a \
--title "The Command Line ${date}" \
--artist "Thomas Gideon" \
--album "The Command Line" \
--year "${year}" \
--genre "Podcast" \
--writer "Thomas Gideon" \
--comment "Weekly ${type} cast.  Email to feedback@thecommandline.net.  Show notes and license information for this episode at http://thecommandline.net/${post_date}/${slug}/" \
--cover-art ~/Dropbox/Public/color_cover_art.jpg \
cmdln.net_${date}.wav
