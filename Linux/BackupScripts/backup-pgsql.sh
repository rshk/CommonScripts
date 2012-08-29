#!/bin/bash

##------------------------------------------------------------------------------
## PostgreSQL backup script
## This script keeps the database dumps in sync with the current
## databases, without keeping history.
## This is useful to restore on a different PostgreSQL server
##------------------------------------------------------------------------------

CONFIG_FILE=~/.pgsql-backup-rc

PGSQL_INIT_SCRIPT="$( ls -1 /etc/init.d/postgresql* 2>/dev/null | head -1 )"
PGSQL_USER=root
PGSQL_HOST=localhost
PGSQL_PORT=5432
REPOSITORY="/BACKUP/pgsql"
CONFIGURED=0

## Read configuration from file
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo "Creating configuration file $CONFIG_FILE"
    cat > "$CONFIG_FILE" <<EOF
## Configuration file for pgsql-backup.sh
## Autogenerated on $(date +"%F %T %Z")
PGSQL_INIT_SCRIPT="$PGSQL_INIT_SCRIPT"
PGSQL_USER="$PGSQL_USER"
PGSQL_HOST="$PGSQL_HOST"
PGSQL_PORT="$PGSQL_PORT"
REPOSITORY="$REPOSITORY"

## Once configured, set this to 1 in order to continue
CONFIGURED=0
EOF
fi

## Check that configured != 0
if [ "$CONFIGURED" == 0 ]; then
    echo "You need to review configuration in $CONFIG_FILE"
    echo "before running this script!"
    echo "Please check configuration file and run again."
    exit 2
fi

## Print header
echo "Starting PostgreSQL backup"
echo "Repository: $REPOSITORY"

## Create repo dir and purge from old backups
if [ ! -d "$REPOSITORY" ]; then
    echo "Creating repository $REPOSITORY"
    mkdir -p "$REPOSITORY"
fi

echo "Purging old backups..."
rm -fr "$REPOSITORY"/*


## Check that service is running..
if ! "$PGSQL_INIT_SCRIPT" status &>/dev/null; then
    echo "PostgreSQL is not running - starting"
    "$PGSQL_INIT_SCRIPT" start
fi


## Get list of databases
ALL_DATABASES="$( psql -U"$PGSQL_USER" -qt -l | awk '{ print $1 }' )"

umask 277

for DATABASE in $ALL_DATABASES; do
    echo -e "Dump db: \e[1;33m$DATABASE\e[0m ... "

    ## -- Plain (SQL) dump
    OUTFILE="${REPOSITORY}/pgsql_${DATABASE}.psql"
    echo -n "  Creating plain dump of $DATABASE ... "
    pg_dump --clean -Fp "${DATABASE}" -U"${PGSQL_USER}" > "${OUTFILE}"
    RET=$?

    echo -en "\e[60G"
    if [ "$RET" == "0" ]; then
        echo -e "[\e[1;32m  OK  \e[0m]"
    else
        echo -e "[\e[1;31mFAILED\e[0m]"
    fi
    echo "    Saved to ${OUTFILE}"

    ## -- binary/tar dump
    OUTFILE="${REPOSITORY}/pgsql_${DATABASE}.backup"
    echo -n "  Creating tar dump of $DATABASE ... "
    pg_dump --clean -Ft "${DATABASE}" -U"${PGSQL_USER}" > "${OUTFILE}"
    RET=$?

    echo -en "\e[60G"
    if [ "$RET" == "0" ]; then
        echo -e "[\e[1;32m  OK  \e[0m]"
    else
        echo -e "[\e[1;31mFAILED\e[0m]"
    fi
    echo "    Saved to ${OUTFILE}"

    echo
done
