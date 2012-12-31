#!/bin/bash

BASEDIR="$( dirname "$0" )"

echo "Copying sources.list"
cp "$BASEDIR"/apt-sources-list-d/*.list /etc/apt/sources.list.d/

echo "Copying preferences"
cp "$BASEDIR"/apt-preferences-d/*.pref /etc/apt/preferences.d/

echo "Adding repository keys"
for keyfile in "$BASEDIR"/apt-keys/*.asc; do
    cat "$keyfile" | apt-key add -
done

## For PostgreSQL
# apt-get install pgdg-keyring
