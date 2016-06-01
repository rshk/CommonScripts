#!/usr/bin/env python

"""
Script to parse TRACE iptables messages from syslog and display output
in a more readable fashion.
"""

import os
import shlex
import subprocess
import sys


IPTABLES = ['iptables']
if 'IPTABLES' in os.environ:
    IPTABLES = shlex.split(os.environ['IPTABLES'])


# Aug 27 15:44:28 infrastructure kernel: TRACE: mangle:PREROUTING:rule:1 IN=red0 OUT= MAC=00:15:5d:24:58:05:00:1b:17:00:01:31:08:00 SRC=77.72.198.97 DST=193.205.196.227 LEN=52 TOS=0x00 PREC=0x00 TTL=58 ID=55053 DF PROTO=TCP SPT=35519 DPT=443 SEQ=2503161252 ACK=2924600051 WINDOW=8180 RES=0x00 ACK URGP=0 OPT (0101080A299AA81307BD9110)   # noqa


class RecordInfo(object):
    def __init__(self):
        self.table = None
        self.chain = None
        self.action = None
        self.lineno = None
        self.attrs = {}
        self.flags = []

    def __repr__(self):
        info = [
            'table={0}'.format(self.table),
            'chain={0}'.format(self.chain),
            'action={0}'.format(self.action),
            'lineno={0}'.format(self.lineno),
        ]
        for k, v in sorted(self.attrs.iteritems()):
            info.append('{0}={1}'.format(k, v))
        for f in self.flags:
            info.append(f)
        return '<{0}({1})>'.format(self.__class__.__name__, ' '.join(info))


for line in sys.stdin:
    startpos = line.find('TRACE:')
    if startpos < 0:
        continue
    tokens = iter(line[startpos:].split())
    assert next(tokens) == 'TRACE:'

    location = next(tokens).split(':')
    assert len(location) == 4

    record = RecordInfo()
    record.table = location[0]
    record.chain = location[1]
    record.action = location[2]
    record.lineno = location[3]

    for tok in tokens:
        if '=' in tok:
            key, val = tok.split('=', 1)
            record.attrs[key] = val

        elif tok == 'OPT':
            record.attrs['OPT'] = next(tokens)

        else:
            record.flags.append(tok)

    print(record)
