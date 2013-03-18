#!/bin/bash

BASEDIR="$( dirname "$0" )"
RELEASE="$( lsb_release -sc )"

echo "Copying sources.list"
cp "$BASEDIR"/apt-sources-list-d/all/*.list /etc/apt/sources.list.d/
if [ -d "$BASEDIR"/apt-sources-list-d/"$RELEASE"/ ]; then
	cp "$BASEDIR"/apt-sources-list-d/"$RELEASE"/*.list /etc/apt/sources.list.d/
else
	echo "WARNING! No release-specific folder found for $RELEASE"
fi

echo "Copying preferences"
cp "$BASEDIR"/apt-preferences-d/*.pref /etc/apt/preferences.d/

echo "Adding repository keys"
for keyfile in "$BASEDIR"/apt-keys/*.asc; do
    cat "$keyfile" | apt-key add -
done

## For PostgreSQL
# apt-get install pgdg-keyring
