#!/usr/bin/env bash

IMAGES=data/*/*/*
for f in $IMAGES
do
    echo "Processing $f"
    mogrify -resize 500x500 "$f"
done
