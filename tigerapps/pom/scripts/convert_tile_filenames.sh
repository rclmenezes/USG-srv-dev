#!/bin/bash

x=0
for fname in `ls -1 ../../static/pom/img/tiles`; do
    Y=$(($x % 11))
    X=$(($x / 11))
    cp ../../static/pom/img/tiles/$fname ../../static/pom/img/tiles/4-$Y-$X.png
    x=$(($x+1))
done
