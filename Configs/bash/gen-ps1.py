#!/usr/bin/env python

"""

Generate a nice prompt for bash, taking colors from the hash
of user / host names.

To use, put this in your .bashrc:

eval $( python /opt/CommonScripts/Configs/bash/gen-ps1.py )

"""

import socket
import getpass
import hashlib
import sys
import os


def prompt_256color(userstring):
    sha = hashlib.sha1(userstring).digest()
    ## 256 colors are: ]x1b[38;5;<n>m where <n> is
    ## 16 + 36 * r + 6 * g + b
    ## and 0 <= (r, g, b) <= 5

    def get_color(ch):
        ## Take a number 0-255 and convert to 0-5
        return int(round(ord(ch) * 5 / 255))

    def color_to_ansi(r, g, b):
        color = 16 + (36 * r) + (6 * g) + b
        return '\\[\\033[38;5;{0}m\\]'.format(color)

    user_color = color_to_ansi(*map(get_color, sha[0:3]))
    host_color = color_to_ansi(*map(get_color, sha[3:6]))
    path_color = color_to_ansi(*map(get_color, sha[6:9]))

    p_color = '\\[\\033[1;33m\\]'
    reset_color = '\\[\\033[0m\\]'

    return "{0}\\u{1}@\\h {2}\\w\\n{3}\\${4} ".format(
        user_color, host_color, path_color, p_color, reset_color)


def prompt_color(userstring):
    sha = hashlib.sha1(userstring).digest()

    def get_color(ch):
        ## Take a number 0-255 and convert to 1-7
        return int(round(ord(ch) * 6 / 255)) + 1

    def color_to_ansi(color):
        color = min(max(1, color), 7)
        return '\\[\\033[{0}m\\]'.format(30 + color)

    user_color = color_to_ansi(*map(get_color, sha[0]))
    host_color = color_to_ansi(*map(get_color, sha[1]))
    path_color = color_to_ansi(*map(get_color, sha[2]))

    p_color = '\\[\\033[1;33m\\]'
    reset_color = '\\[\\033[0m\\]'

    return "{0}\\u{1}@\\h {2}\\w\\n{3}\\${4} ".format(
        user_color, host_color, path_color, p_color, reset_color)


def prompt_default(userstring):
    return "\\u@\\h \\w\\n\\$ "


if len(sys.argv) > 1:
    userstring = sys.argv[1]
else:
    userstring = '{0}@{1}'.format(getpass.getuser(), socket.gethostname())

print('case "$TERM" in')

print('xterm-256color)')
print("PS1='{0}'".format(prompt_256color(userstring)))
print(';;')

print('xterm-color)')
print("PS1='{0}'".format(prompt_color(userstring)))
print(';;')

print('*)')
print("PS1='{0}'".format(prompt_default(userstring)))
print(';;')

print('esac')
