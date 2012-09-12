#!/bin/bash

emerge --sync && \
    layman -s ALL && \
    eix-update && \
    eupdatedb && \
    emerge --update --newuse --deep --with-bdeps=y @world && \
    revdep-rebuild

echo "Now, you can run 'emerge --depclean'"
