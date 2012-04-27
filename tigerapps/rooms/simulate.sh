#!/bin/bash
manager=~/USG-srv-dev/tigerapps/manage.py
# Reset availability
$manager rooms_resetavail
crontab -l > tab.tmp
echo -e "* * * * * $manager rooms_updateavail $1 $2\n" >> tab.tmp
echo "Installing new crontab updating by $1 every minute"
crontab < tab.tmp
