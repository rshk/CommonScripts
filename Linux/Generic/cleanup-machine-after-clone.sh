#!/bin/bash

# This will clean up a machine after cloning..

echo "Actions cannot be recoveried."
read -p "Are you sure? [y/N] " CONF
if [ "$CONF" != "y" ]; then
    echo "Aborted"
    exit 1
fi

echo "Removing persistent UDEV rules"
rm /etc/udev/rules.d/70-persistent-*.rules

echo "Removing bash history for all users"
cat /etc/passwd | cut -d: -f6 | sed 's@$@/.bash_history@' | xargs -d '\n' rm -fv

echo "Regenerating SSH keys (assuming debian/ubuntu)"
rm -fv /etc/ssh/ssh_host_*
dpkg-reconfigure openssh-server
