#!/usr/bin/env python

from __future__ import print_function

import io
import re
import subprocess
import shlex
import os


IPTABLES = ['iptables']
if 'IPTABLES' in os.environ:
    IPTABLES = shlex.split(os.environ['IPTABLES'])

TABLES = ['filter', 'nat', 'mangle', 'raw']


def col256(text, fg=None, bg=None):
    if not isinstance(text, unicode):
        text = unicode(text, encoding='utf-8')
    buf = io.StringIO()
    if fg is not None:
        buf.write(u'\x1b[38;5;{0:d}m'.format(fg))
    if bg is not None:
        buf.write(u'\x1b[48;5;{0:d}m'.format(bg))
    buf.write(text)
    buf.write(u'\x1b[0m')
    return buf.getvalue()


def strlen_no_colors(s):
    """Calculate length of a string, stripping colors"""
    return len(re.sub(r'\x1b\[[^m]+m', '', s))


def format_table(rows):
    col_widths = {}
    for row in rows:
        for i, col in enumerate(row):
            col_widths[i] = max(col_widths.get(i, 0), strlen_no_colors(col))

    output = io.StringIO()
    for row in rows:
        for i, col in enumerate(row):
            width = col_widths[i]
            padding = width - strlen_no_colors(col)
            if not isinstance(col, unicode):
                col = unicode(col, encoding='utf-8')
            output.write(col)
            output.write(u' ' * padding)
            output.write(u'   ')  # Column separator
        output.write(u'\n')
    return output.getvalue()


def rescale(X, A, B, C, D, force_float=False):
    retval = ((float(X - A) / (B - A)) * (D - C)) + C
    if not force_float and all(type(x) == int for x in [X, A, B, C, D]):
        return int(round(retval))
    return retval


def _split_blocks(lines):
    buf = []
    for line in lines:
        if line.strip() == '':
            if len(buf):
                yield buf
                buf = []
        else:
            buf.append(line)
    if len(buf):
        yield buf


def _colorize_chain_header(line):
    regex = r"^(?P<prefix>Chain\s+)(?P<name>[^\s]+)\s*\((?P<attrs>.*)\)"  # noqa
    matches = re.match(regex, line.rstrip())

    data = matches.groupdict()
    data['attrs'] = data['attrs'].replace('ACCEPT', col256('ACCEPT', fg=82))
    data['attrs'] = data['attrs'].replace('DROP', col256('DROP', fg=160))

    return (
        u"\033[48;5;235m\033[K"
        u"\033[1m{prefix}\033[0m"
        u"\033[48;5;20m\033[38;5;255m {name} \033[0m"
        u" ({attrs})\n"
        .format(**data))


def _colorize_table_header(row):
    return ['\033[4m' + col256(col, fg=245) for col in row]


def _colorize_number(num):
    exps = {'': 1, 'K': 1024, 'M': 1024 ** 2, 'G': 1024 ** 3, 'T': 1024 ** 4}
    matches = re.match(r'^(?P<num>[0-9]+)(?P<exp>[A-Za-z]*)$', num)
    if not matches:
        return col256(num, fg=88)
    numval = int(matches.groupdict()['num'])

    exp = matches.groupdict()['exp']
    if exp in exps:
        numval *= exps[exp]
    else:
        return col256(num, fg=88)

    color = int(rescale(numval, 0, 1024 ** 3, 240, 255))
    color = min(color, 255)

    return col256(num, fg=color)


def _colorize_target_name(name):
    if name == 'ACCEPT':
        return col256(name, fg=82)
    if name in ('DROP', 'REJECT'):
        return col256(name, fg=160)
    if name == 'RETURN':
        return col256(name, fg=33)
    if name in ('DNAT', 'SNAT', 'MASQUERADE'):
        return col256(name, fg=92)
    if name == 'LOG':
        return col256(name, fg=87)
    return col256(name, fg=166)


def _colorize_protocol(proto):
    if proto == 'all':
        return col256(proto, fg=240)
    if proto == 'tcp':
        return col256(proto, fg=178)
    if proto == 'udp':
        return col256(proto, fg=27)
    if proto == 'icmp':
        return col256(proto, fg=28)
    return proto


def _colorize_options(opt):
    if opt == '--':
        return col256(opt, fg=240)
    return opt


def _colorize_interface(intf):
    if intf == '*':
        return col256(intf, fg=240)
    if intf.startswith('green'):
        return col256(intf, fg=34)
    if intf.startswith('red'):
        return col256(intf, fg=160)
    if intf.startswith('tun'):
        return col256(intf, fg=27)
    if intf == 'lo':
        return col256(intf, fg=184)
    return intf


def _colorize_addr(addr):
    if addr == '0.0.0.0/0':
        return col256(addr, fg=240)
    return addr


def _colorize_extras_token(tok):
    if re.match(r'^[0-9]+$', tok):
        return col256(tok, 45)
    if re.match(r'^0x[0-9]+$', tok):
        return col256(tok, 48)
    # todo: highlight:
    # dpt:<port> dpts:<port>:<port>
    # spt:<port> spts:<port>:<port>
    # to:<ip> to:<ip>:<port>
    # from:<ip> from:<ip>:<port>
    return tok


def _colorize_extras(extras):
    tokens = iter(extras.split())
    output = io.BytesIO()
    for tok in tokens:
        if tok == '/*':
            output.write('\x1b[38;5;240m')
            output.write(tok)
            for tok1 in tokens:
                output.write(tok1)
                if tok1 == '*/':
                    output.write('\x1b[0m')
                    break

        elif tok.startswith('"'):
            output.write('\x1b[38;5;190m')
            output.write(tok)
            for tok1 in tokens:
                output.write(tok1)
                if tok1.endswith('"'):
                    output.write('\x1b[0m')
                    break
        else:
            output.write(_colorize_extras_token(tok).encode('utf-8'))

        output.write(' ')

    # extras = re.sub(r'(/\*.*\*/)', '\x1b[38;5;240m\\1\x1b[0m', extras)
    return output.getvalue()


def _colorize_table_row(row):
    return [
        col256(format(row[0], '>3'), fg=250, bg=238),  # num
        _colorize_number(row[1]),  # pkts
        _colorize_number(row[2]),  # bytes
        _colorize_target_name(row[3]),  # target
        _colorize_protocol(row[4]),  # prot
        _colorize_options(row[5]),  # opt
        _colorize_interface(row[6]),  # in
        _colorize_interface(row[7]),  # out
        _colorize_addr(row[8]),  # source
        _colorize_addr(row[9]),  # destination
        _colorize_extras(' '.join(row[10:])),
    ]


def colorize_output(lines):
    output = io.StringIO()
    for block in _split_blocks(lines):
        chain_line = block[0]
        output.write(_colorize_chain_header(chain_line))

        table_header = block[1].split()
        table_header = _colorize_table_header(table_header)
        table_rows = [x.split() for x in block[2:]]
        table_rows = [_colorize_table_row(t) for t in table_rows]
        output.write(format_table([table_header] + table_rows))

        output.write(u'\n')

    return output.getvalue()


for table in TABLES:
    output = subprocess.check_output(IPTABLES + [
        '-t', table, '--list', '--line-numbers', '-v', '-n'])
    print("\033[48;5;124m\033[K Table: \033[1m{0} \033[0m\n".format(table))
    print(colorize_output(iter(output.splitlines())).encode('utf-8'))
