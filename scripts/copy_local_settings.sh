#!/bin/bash

echo "Enter your username on this server:"
read username
home="/home/$username/USG-srv-dev"
echo "This may overwrite any existing local_settings.py files in all subdirectories of $home. Continue? [y/n]"
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
