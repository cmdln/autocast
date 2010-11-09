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

src=$1/contents.xml  
shift
target=$1
# copy .gz file based on arg
cp "$src" ./contents.xml.gz
echo "Copied $src to ./contents.xml.gz"

# gunzip original file
gunzip contents.xml.gz
echo "Gunzipped contents.xml.gz"

# makes sure the ns is only on one line, also
# makes the interim file more readable for debugging
tidy -config tidyrc -xml -m contents.xml
echo "Tidied contents.xml"

# xalan doesn't handle ns well, stripp them
sed -e "s/ xmlns=\".*\"//g" -i contents.xml
# xalan also doesn't handle imports, which shouldn't be necessary anyway
sed -e "s/ standalone=\"no\"//g" -i contents.xml

# use grep to figure out which xsl to use
grep "<lit>[0-9]\{2\}:[0-9]\{2\}</lit>" contents.xml > /dev/null
if [ "$?" == "0" ]
then
    xsl=with_offset.xsl
else
    xsl=without_offset.xsl
fi
xalan -xsl $xsl -in contents.xml -text -out contents.txt

# expand the indent counts to proper leading white space
sed -e "s/^2/    /" -i contents.txt
sed -e "s/^3/        /" -i contents.txt
sed -e "s/^4/            /" -i contents.txt
sed -e "s/^5/                /" -i contents.txt
sed -e "s/^6/                    /" -i contents.txt

# snug the result where requested
mv contents.txt "$target"
# clean up the temporary files
rm contents.xml
