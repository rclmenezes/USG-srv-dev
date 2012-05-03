#!/bin/bash

python cut.py buildings_hover.png building_metadata.csv h /srv/tigerapps/static/pom/img/bldgs/
python cut.py buildings_event_hover.png building_metadata.csv eh /srv/tigerapps/static/pom/img/bldgs/
python cut.py buildings_event.png building_metadata.csv e /srv/tigerapps/static/pom/img/bldgs/
python cut.py buildings_default.png building_metadata.csv '' /srv/tigerapps/static/pom/img/bldgs/
