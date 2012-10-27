#!/bin/bash

## Set prompt based on hostname and username

HOST_CKSUM="$( echo "${USER}@${HOSTNAME}" | cksum )"
C1="$[ 31 + $( echo "$HOST_CKSUM" | cut -c1-3 | sed 's/^0*//' ) % 6 ]"
C2="$[ 31 + $( echo "$HOST_CKSUM" | cut -c4-6 | sed 's/^0*//' ) % 6 ]"
C3="$[ 31 + $( echo "$HOST_CKSUM" | cut -c7-9 | sed 's/^0*//' ) % 6 ]"
#export PS1="\[\e[1;${C1}m\]\h\[\e[0m\] \[\e[1;${C2}m\]\u\[\e[0m\] : \[\e[1;${C3}m\]\w\[\e[0m\]\n\[\e[1;31m\]\\$\[\e[0m\] "
export PS1="\[\e[1;${C2}m\]\u\[\e[0m\]@\[\e[1;${C1}m\]\h\[\e[0m\] \[\e[0;${C3}m\]\w\[\e[0m\]\n\[\e[1;31m\]\\$\[\e[0m\] "
unset HOST_CKSUM C1 C2 C3
