#!/bin/bash
# TODO copy .gz file based on arg
# TODO gunzip original file
xalan -xsl outline.xsl -in contents.xml -text -out contents.txt
sed -e "s/^2/    /" -i contents.txt
sed -e "s/^3/        /" -i contents.txt
sed -e "s/^4/            /" -i contents.txt
sed -e "s/^5/                /" -i contents.txt
sed -e "s/^6/                    /" -i contents.txt
less contents.txt
