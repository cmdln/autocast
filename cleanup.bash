#!/bin/bash
prefix=$1

if [ -z $prefix ]
then
	echo "Must specific a prefix."
	exit 1
fi

function clean_old() {
	prefix=$1
	ext=$2
	to_keep=$3
	ls $prefix*$ext 1> /dev/null 2>&1
	clean=$?
	count=0
	if [ 0 -eq $clean ]
	then
		for file in $(ls -r $prefix*$ext)
		do
			if [ $count -lt $to_keep ]
			then
				count=$((count + 1))
			else
				rm $file
			fi
		done
	fi
}

function clean_ext() {
	ls $1*$2 1> /dev/null 2>&1
	clean=$?
	if [ 0 -eq $clean ]
	then
		rm $1*$2
	fi
}

clean_old $prefix "wav" 2
clean_old $prefix "mp3.xml.*" 1
clean_old $prefix "m4a.xml.*" 1
clean_old $prefix "ogg.xml.*" 1

clean_ext $prefix "mp3" 
clean_ext $prefix "chapters.txt" 
clean_ext $prefix "m4a"
clean_ext $prefix "ogg"
clean_ext $prefix "flac"

