#!/bin/bash

######################################################################
## Executes DRUSH on all sites contained in a given Drupal
## installation directory.
## Created: 2011-09-06 Samu
######################################################################

DRUSH=/opt/drush/drush
DRUPALDIR="$( pwd )"

[ -f ~/.drupal-scripts-rc ] && source ~/.drupal-scripts-rc

cd "$DRUPALDIR"

for site in $( $DRUSH sa ); do
    echo -e "Running DRUSH on \e[1;33m$site\e[0m ..."
    $DRUSH -l "$site" "$@"
    echo
done
