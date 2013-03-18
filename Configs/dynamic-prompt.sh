#!/bin/bash

## Set prompt color based on hostname and username hash

source "$( dirname "$0" )"/bash_prompt

HOST_CKSUM="$( echo "${USER}@${HOSTNAME}" | cksum )"
C1="$[ 31 + $( echo "$HOST_CKSUM" | cut -c1-3 | sed 's/^0*//' ) % 6 ]"
C2="$[ 31 + $( echo "$HOST_CKSUM" | cut -c4-6 | sed 's/^0*//' ) % 6 ]"
C3="$[ 31 + $( echo "$HOST_CKSUM" | cut -c7-9 | sed 's/^0*//' ) % 6 ]"
#export PS1="\[\e[1;${C1}m\]\h\[\e[0m\] \[\e[1;${C2}m\]\u\[\e[0m\] : \[\e[1;${C3}m\]\w\[\e[0m\]\n\[\e[1;31m\]\\$\[\e[0m\] "
#export PS1="\[\e[1;${C2}m\]\u\[\e[0m\]@\[\e[1;${C1}m\]\h\[\e[0m\] \[\e[0;${C3}m\]\w\[\e[0m\]\n\[\e[1;31m\]\\$\[\e[0m\] "

export NICEPROMPT_BASEPROMPT='\n\
` niceprompt_lastcommandfailed `\
\033[0;37m\033[1;'"$C2"'m\u\
\033[1;'"$C1"'m@\h\033[0;37m \033[0m\
\033['"$C3"'m\w\033[0m\
` niceprompt_vcprompt `\
` niceprompt_backgroundjobs `\
` niceprompt_chroot `\
` niceprompt_virtualenv `\
` niceprompt_ssh `\
` niceprompt_screen `\
\033[0m'
export PS1="\033[G${NICEPROMPT_BASEPROMPT}
\[\033[1;32m\]\\\$\[\033[0m\] "

unset HOST_CKSUM C1 C2 C3
