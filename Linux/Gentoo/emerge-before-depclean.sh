#!/bin/bash

emerge --update --newuse --deep --with-bdeps=y @world

if which revdep-rebuild &>/dev/null; then
    revdep-rebuild
else
    echo "revdep-rebuild not found -- install app-portage/gentoolkit"
fi
