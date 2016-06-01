#!/bin/zsh

SIZE=1920x

ERRORS=

if ! which eog > /dev/null; then
    echo "Dependency missing: eog"
    ERRORS=1
fi

if ! which convert > /dev/null; then
    echo "Dependency missing: convert (from ImageMagck)"
    ERRORS=1
fi

if ! which zenity > /dev/null; then
    echo "Dependency missing: zenity"
    ERRORS=1
fi


if [[ "$ERRORS" == "1" ]]; then
    exit 1
fi

for arg in $@; do
    echo "Resizing $arg to $SIZE"
    LOGFILE="$( mktemp --suffix=.log )"
    OUTFILE="$( mktemp --suffix=.jpg )"
    if convert -scale $SIZE $arg $OUTFILE &> $LOGFILE; then
        eog $OUTFILE
    else
        zenity --info \
               --text="<b>Error converting $arg</b>\n\n$( cat $LOGFILE )" \
               --title "Error converting image" \
               --icon-name=error
    fi
    rm -f $LOGFILE $OUTFILE
done
