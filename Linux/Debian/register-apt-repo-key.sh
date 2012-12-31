#!/bin/bash

# Copyright (c) 2010-2012 Samuele ~redShadow~ Santi
# redshadow&hackzine.org - http://www.hackzine.org
# Under Gnu GPL v3

KEYID="$1"

if [ -z "$KEYID" ]; then
    echo "Usage: $( basename "$0" ) <keyid>"
    exit 1
fi

echo "Registering APT key $1..."
gpg --keyserver pgp.mit.edu --recv-keys "$KEYID"
gpg --export --armor "$KEYID" | apt-key add -
