#!/bin/bash

## Runs emerge --sync, then updates layman, eix and esearch
## databases.

if [ "$1" == "--help" ]; then
  echo "$0 - runs emerge --sync, update-eix and eupdatedb"
  exit 0
fi

echo -e "\n--- Syncing portage tree --------------------------------------"
/usr/bin/emerge --sync
echo

if which layman &>/dev/null; then
    echo "--- Updating layman overlays ----------------------------------"
    layman -s ALL
    echo
else
    echo "Layman not found"
fi

if which eix-update &>/dev/null; then
    echo "--- Updating eix database--------------------------------------"
    eix-update
    echo
else
    echo "eix-update not found"
fi

if which eupdatedb; then
    echo "--- Updating esearch database ---------------------------------"
    eupdatedb
    echo
else
    echo "eupdatedb not found"
fi
