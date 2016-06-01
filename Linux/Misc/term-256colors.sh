#!/bin/bash
for i in {0..255}; do echo -e '\033[38;5;'$i'm Color: '$i'\033[0m \033[48;5;'$i'm Color: '$i'\033[0m'; done
