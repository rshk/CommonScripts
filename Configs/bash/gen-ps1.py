#!/usr/bin/env python

"""
Generate a nice prompt for bash, taking colors from the hash
of user / host names.

To use, put this in your .bashrc:

eval $( python /opt/CommonScripts/Configs/bash/gen-ps1.py )
"""

from __future__ import print_function, division

import socket
import getpass
import hashlib
import sys
import colorsys
import struct
import os


# Utilities
#--------------------

def color_luminance(r, g, b):
    """
    Calculate the apparent luminance of a RGB color

    :param r: red component (0 <= r <= 1)
    :param g: green component (0 <= r <= 1)
    :param b: blue component (0 <= r <= 1)
    :return: the relative luminance (0 <= luminance <= 1)
    """
    return (0.2126 * r) + (0.7152 * g) + (0.0722 * b)


def color_to_8bit(r, g, b):
    """
    Convert a (r, g, b) color (where 0 <= r,g,b <= 1)
    to a 8 bit color.
    """
    r, g, b = (int(x * 5) for x in (r, g, b))
    return 16 + int(round(r * 36 + 6 * g + b))


def color_from_8bit(color):
    """Convert 8bit color to float three-tuple"""
    color -= 16
    r = color / 36
    g = color / 6 % 6
    b = color % 6
    return tuple(x / 6 for x in (r, g, b))


# Prompt generators
#--------------------


def prompt_256color(userstring):
    sha = hashlib.sha1(userstring).digest()

    # 256 colors are: ]x1b[38;5;<n>m where <n> is
    # 16 + 36 * r + 6 * g + b
    # and 0 <= (r, g, b) <= 5

    # The colors should be in the range 16-231

    # Calculate "seeds" to generate colors
    _user_seed = struct.unpack('!I', sha[0:4])[0]
    _host_seed = struct.unpack('!I', sha[4:8])[0]
    _path_seed = struct.unpack('!I', sha[8:12])[0]

    maxint = 256 ** 4

    color_range = (16, 231)
    color_range_delta = color_range[1] - color_range[0]

    user_color = _user_seed * (color_range_delta) / maxint + color_range[0]
    user_rgb = color_from_8bit(user_color)
    user_lum = color_luminance(*user_rgb)
    user_fg_color = '37' if user_lum < 0.35 else '30'

    host_color = _host_seed * (color_range_delta) / maxint + color_range[0]
    host_rgb = color_from_8bit(host_color)
    host_lum = color_luminance(*host_rgb)
    host_fg_color = '37' if host_lum < 0.35 else '30'

    # We only want colors with luminance > .35 !
    path_color = _path_seed * color_range_delta / maxint + color_range[0]
    path_rgb = color_from_8bit(path_color)
    path_hsv = colorsys.rgb_to_hsv(*path_rgb)
    if path_hsv[2] < .5:
        path_hsv = path_hsv[:2] + (.5,)
        path_rgb = colorsys.hsv_to_rgb(*path_hsv)
        path_color = color_to_8bit(*path_rgb)

    # Let's convert 'em to integers!
    user_color = int(round(user_color))
    host_color = int(round(host_color))
    path_color = int(round(path_color))

    user_color = '\\[\\033[48;5;{0}m\\033[{1}m\\]'\
        .format(user_color, user_fg_color)
    host_color = '\\[\\033[48;5;{0}m\\033[{1}m\\]'\
        .format(host_color, host_fg_color)
    path_color = '\\[\\033[38;5;{0}m\\]'.format(path_color)
    dollar_color = '\\[\\033[1;33m\\]'
    reset_color = '\\[\\033[0m\\]'

    return "{uc} \\u{hc}@\\h {rc} {pc}\\w{rc}\\n{sc}\\${rc} ".format(
        uc=user_color,  # \u color
        hc=host_color,  # \h color
        pc=path_color,  # \w color
        sc=dollar_color,  # \$ color
        rc=reset_color)  # reset color


def prompt_color(userstring):
    # todo: this should be a limited color version of the 256 color prompt
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


def do_demo():
    import string
    import random

    print("Demo mode\n\n")

    def _random_name():
        letters = string.ascii_lowercase + string.digits
        string_length = random.randint(3, 15)
        return ''.join(random.choice(letters) for x in xrange(string_length))

    for i in xrange(10):
        user = _random_name()
        host = _random_name()
        path = '/'.join(_random_name() for x in xrange(random.randint(1, 10)))

        prompt = prompt_256color('@'.join((user, host)))
        prompt = prompt.replace('\\u', user)
        prompt = prompt.replace('\\h', host)
        prompt = prompt.replace('\\w', path)
        prompt = prompt.replace('\\$', '$')
        prompt = prompt.replace('\\[', '')
        prompt = prompt.replace('\\]', '')
        prompt = eval("'" + prompt + "'")  # Ugly but should work!
        print(prompt, "\n\n")


def do_print_prompt():
    if len(sys.argv) > 1:
        userstring = sys.argv[1]
    else:
        userstring = '{0}@{1}'.format(getpass.getuser(), socket.gethostname())
        prompt_seed = os.environ.get('PROMPT_SEED')
        if prompt_seed is not None:
            # Allow "seeding" the prompt, to avoid ugly colors...
            userstring = '{0}:{1}'.format(prompt_seed, userstring)

    print('case "$TERM" in')

    print('xterm-256color|screen)',
          "PS1='{0}'".format(prompt_256color(userstring)), ';;')

    print('xterm-color)',
          "PS1='{0}'".format(prompt_color(userstring)), ';;')

    print('*)',
          "PS1='{0}'".format(prompt_default(userstring)), ';;')

    print('esac')


def do_test_contrast():
    # We print a matrix of 16 x 16 color
    reset = "\x1b[0m"
    for x in xrange(16):
        for y in xrange(16):
            color = x + y * 16
            bg_color = "\x1b[48;5;{0}m".format(color)

            rgb = color_from_8bit(color)
            lum = color_luminance(*rgb)
            fg_color = "\x1b[37m" if (lum < 0.35) else "\x1b[30m"
            print("{bg}{fg} {col:3d} {rst}".format(
                bg=bg_color, fg=fg_color, col=color, rst=reset, lum=lum),
                end=" ")
        print()


def main():
    if '--demo' in sys.argv:
        do_demo()
        return
    if '--test-contrast' in sys.argv:
        do_test_contrast()
        return
    do_print_prompt()


if __name__ == '__main__':
    main()
