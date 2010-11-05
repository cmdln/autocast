#!/bin/bash
function restore {
backup=${1}.$(date +%Y-%m-%d)
	if [ -f "$backup" ]
	then
		echo "Restoring $backup"
		mv ${1}.$(date +%Y-%m-%d) ${1}
	fi
}
restore cmdln_mp3.xml
restore cmdln_m4a.xml
restore cmdln_ogg.xml
