#!/bin/bash

## Set prompt based on hostname

HOST_CKSUM="$( hostname | cksum )"
C1="$[ 31 + 1$( echo "$HOST_CKSUM" | cut -c1-3 ) % 6 ]"
C2="$[ 31 + 1$( echo "$HOST_CKSUM" | cut -c4-6 ) % 6 ]"
C3="$[ 31 + 1$( echo "$HOST_CKSUM" | cut -c7-9 ) % 6 ]"
export PS1="\[\e[1;${C1}m\]\h\[\e[0m\] \[\e[1;${C2}m\]\u\[\e[0m\] : \[\e[1;${C3}m\]\w\[\e[0m\]\n\[\e[1;31m\]\\$\[\e[0m\] "
unset HOST_CKSUM C1 C2 C3
