#!/bin/bash

emerge --sync && \
    layman -s ALL && \
    eix-update && \
    eupdatedb && \
    emerge --update --newuse --deep --with-bdeps=y @world && \
    emerge --depclean && \
    revdep-rebuild
