#!/bin/bash

home="$HOME/USG-srv-dev"
echo "This will overwrite any existing local_settings.py files in all subdirectories of $home with the local_settings.py files in /srv. Continue? [y/n]"
read to_continue
if [[ $to_continue != 'y' ]]; then
    echo "Did not enter 'y': will not copy"
    exit
fi

for folder in `ls -l $home | grep ^d | awk '{ print $NF; }'`; do
    for file in `find /srv/$folder | grep local_settings.py`; do
        echo "cp $file $home/${file:5}"
        cp $file $home/${file:5}
    done
done
