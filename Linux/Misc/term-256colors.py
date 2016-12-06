#!/usr/bin/env python3

from __future__ import print_function


def b6(r, g, b):
    return r * 36 + g * 6 + b + 16


def format_cell(c):
    r, g, b = c
    color = b6(r, g, b)
    return ('\x1b[48;5;{}m\x1b[38;5;{}m {:3s} \x1b[0m'
            .format(color, 255 if is_dark(r, g, b) else 232, str(color)))


def luminance(r, g, b):
    return (0.299 * r / 5) + (0.587 * g / 5) + (0.114 * b / 5)


def is_dark(r, g, b):
    return luminance(r, g, b) < .4


if __name__ == '__main__':
    for c1 in range(6):
        for c2 in range(6):
            for perm in range(3):
                for c3 in range(6):
                    if perm == 0:
                        color = (c1, c2, c3)
                    elif perm == 1:
                        color = (c2, c3, c1)
                    elif perm == 2:
                        color = (c3, c1, c2)
                    print(format_cell(color), end='')
                print('  ', end='')
            print()
        print()
