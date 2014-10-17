#!/usr/bin/env python

from __future__ import print_function

import hashlib
import io
import os
import re
import shlex
import subprocess


IPTABLES = ['iptables']
if 'IPTABLES' in os.environ:
    IPTABLES = shlex.split(os.environ['IPTABLES'])

TABLES = ['filter', 'nat', 'mangle', 'raw']

SYSTEM_TARGET_COLORS = {
    'ACCEPT': (255, '020'),
    'DROP': (255, '200'),
    'REJECT': (255, '200'),
    'RETURN': (255, '003'),
    'DNAT': (255, '204'),
    'SNAT': (255, '204'),
    'MASQUERADE': (255, '204'),
    'LOG': ('155', '000'),
}

COLOR_IP = '051'
COLOR_PORT = '054'
COLOR_NETMASK = '510'


def col256(text, fg=None, bg=None):
    if not isinstance(text, unicode):
        text = unicode(text, encoding='utf-8')
    buf = io.StringIO()
    if fg is not None:
        buf.write(u'\x1b[38;5;{0:d}m'.format(_to_color(fg)))
    if bg is not None:
        buf.write(u'\x1b[48;5;{0:d}m'.format(_to_color(bg)))
    buf.write(text)
    buf.write(u'\x1b[0m')
    return buf.getvalue()


def _to_color(num):
    if isinstance(num, (int, long)):
        return num  # Assume it is already a color

    if isinstance(num, basestring) and len(num) <= 3:
        return 16 + int(num, 6)

    raise ValueError("Invalid color: {0!r}".format(num))


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


def _colorize_chain_name(name):
    h = hashlib.sha1(name).hexdigest()
    color = int(h, 16) % 216
    return ''.join((
        col256('  ', bg=color),
        col256(" {0} ".format(name), bg='335', fg=232)))


def _colorize_chain_header(line):
    regex = r"^(?P<prefix>Chain\s+)(?P<name>[^\s]+)\s*\((?P<attrs>.*)\)"  # noqa
    matches = re.match(regex, line.rstrip())

    data = matches.groupdict()
    data['attrs'] = data['attrs'].replace('ACCEPT', col256('ACCEPT', fg=82))
    data['attrs'] = data['attrs'].replace('DROP', col256('DROP', fg=160))

    return ''.join((
        u"\033[0m",
        col256(" " + data['prefix'], bg=255, fg=232), ' ',
        _colorize_chain_name(data['name']),
        u" ({attrs})\n"
        )).format(**data)


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
    if name in SYSTEM_TARGET_COLORS:
        col = SYSTEM_TARGET_COLORS[name]
        return col256(" {0} ".format(name), fg=col[0], bg=col[1])

    return _colorize_chain_name(name)


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

    m = re.match('^(?P<ip>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})$',
                 addr)
    if m:
        return col256(m.group('ip'), fg=COLOR_IP)

    m = re.match('^(?P<ip>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})$',
                 addr)
    if m:
        return col256(m.group('ip'), fg=COLOR_IP)

    m = re.match('^(?P<ip>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})'
                 '/(?P<netmask>[0-9]+)$',
                 addr)
    if m:
        return ''.join((col256(m.group('ip'), fg=COLOR_IP),
                        col256('/' + m.group('netmask'), fg=COLOR_NETMASK)))

    m = re.match('^(?P<ip>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})'
                 ':(?P<port>[0-9]+)$',
                 addr)
    if m:
        return ''.join((col256(m.group('ip'), fg=COLOR_IP),
                        col256(':' + m.group('port'), fg=COLOR_PORT)))

    return addr


def _colorize_port(port):
    # Can be: <port> or <porte:<port>
    return ':'.join(col256(p, fg=COLOR_PORT) for p in port.split(':'))


def _colorize_extras_token(tok):
    if re.match(r'^[0-9]+$', tok):
        return col256(tok, 45)
    if re.match(r'^0x[0-9]+$', tok):
        return col256(tok, 48)

    if (tok.startswith('dpt:') or tok.startswith('dpts:') or
            tok.startswith('spt:') or tok.startswith('spts:')):

        parts = tok.split(':', 1)
        return parts[0] + ':' + _colorize_port(parts[1])

    if tok.startswith('to:') or tok.startswith('from:'):
        parts = tok.split(':', 1)
        return parts[0] + ':' + _colorize_addr(parts[1])

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
    print("\033[0m\033[48;5;{0}m\033[K Table: \033[1m{1} \033[0m\n"
          .format(_to_color('200'), table))
    print(colorize_output(iter(output.splitlines())).encode('utf-8'))
