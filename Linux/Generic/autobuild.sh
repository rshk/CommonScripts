#!/bin/bash

##------------------------------------------------------------
## Improved, generic auto-builder script
## Author: Samuele Santi
## License: (C)2012 - Under GPL v3 or later
##------------------------------------------------------------

usage() {
cat <<EOF
Usage: $0 [<options>] <command>

OPTIONS
  -h  Show this help and exit

  -w <dir>
      Specify the working directory in which to execute
      the command. (Default: current directory)

  -l <dir>
      Specify in which directory to listen for changes
      (Default: current directory)

  -n 0/1
      Specify whether to enable notifications (Default: 1)
EOF
}

WORKDIR="$PWD"
LISTENDIR="$PWD"
ENABLE_NOTIFY=1

while getopts "hw:l:n:" OPTION; do
    case $OPTION in
	h)
	    usage
	    exit
	    ;;
	w)
	    WORKDIR="$OPTARG"
	    ;;
	l)
	    LISTENDIR="$OPTARG"
	    ;;
	n)
	    ENABLE_NOTIFY="$OPTARG"
	    ;;
	?)
	    echo "Invalid option: -${OPTARG}"
	    usage
	    exit 1
	    ;;
    esac
done

## -- process options

COMMAND="$@"

if [ -z "$COMMAND" ]; then
    echo "You must specify a command!"
    usage
    exit 1
fi

if [ "$ENABLE_NOTIFY" == "1" ] && ! which inotifywait &>/dev/null; then
    echo "WARNING: Program 'inotifywait' is not installed"
    echo "Disabling notifications"
    ENABLE_NOTIFY=0
fi

WORKDIR="$( readlink -f "$WORKDIR" )"
LISTENDIR="$( readlink -f "$LISTENDIR" )"
LISTENSIGNALS="modify,close_write,moved_to,moved_from,move,create,delete"

## -- run stuff

echo "Listening for changes on ${LISTENDIR}"
echo "Will run \`${COMMAND}' upon changes"
echo "------------------------------------------------------------"

fade() {
    sed 's/^\(.*\)$/\x1b[1;30m\1\x1b[0m/'
}

while :; do
    inotifywait -r -e "$LISTENSIGNALS" "$LISTENDIR" 2>&1 | fade
    $COMMAND
    RET="$?"
    if [ "$ENABLE_NOTIFY" -eq "1" ]; then
	if [ "$RET" == "0" ]; then
	    ICO="dialog-information"
	    TITLE="Command execution successful"
	else
	    ICO="dialog-error"
	    TITLE="Command execution failed"
	fi
	notify-send "$TITLE" \
	    "Command was: \`${COMMAND}'\n\nWorkdir: $(pwd)\n\nReturn code: $RET" \
	    --icon="$ICO" \
	    2>&1 | fade
    fi
done
