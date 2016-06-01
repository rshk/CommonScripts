#!/usr/bin/env python

from __future__ import unicode_literals, print_function, division

from math import ceil
import sys
import subprocess
import shlex


usage = """\
shard_args.py <count> <command> [<args> ...]
"""


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]


def partition(items, count):
    pagesize = int(ceil(len(items) / count))
    return chunks(items, pagesize)


def main():
    try:
        count = sys.argv[1]
        command = sys.argv[2]
    except IndexError:
        print(usage)
        return 1
    count = int(count)
    command = shlex.split(command)
    other = sys.argv[3:]

    for i, items in enumerate(partition(other, count)):
        print('{0:4d}: {1}'.format(i, items))
        subprocess.Popen(command + items)


if __name__ == '__main__':
    sys.exit(main())
