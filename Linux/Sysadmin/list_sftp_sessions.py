#!/usr/bin/env python
# -*- coding: utf-8 -*-

import grp
import itertools
import pwd
import re
from datetime import datetime, timedelta

import click
import psutil


def find_processes(name, exclude_uids, include_uids):
    now = datetime.utcnow()
    for proc in psutil.process_iter():

        if proc.name() != name:
            continue

        uid = proc.uids().real

        if uid in exclude_uids:
            continue

        if include_uids and uid not in include_uids:
            continue

        ctime = datetime.utcfromtimestamp(proc.create_time())
        uptime = now - ctime

        yield uptime, proc


def to_seconds(ctx, param, value):
    m = re.match(r'^(?P<num>[0-9]+)(?P<suff>[a-z]*)$', value.lower())
    if not m:
        raise ValueError('Invalid time specification: {}'.format(value))
    suff = m.group('suff')
    mult = {'': 1, 'm': 60, 'h': 3600, 'd': 24 * 3600}[suff]
    return int(m.group('num')) * mult


def set_of_users(ctx, param, value):
    resolved = [_resolve_users_group(x) for x in value]
    chained = itertools.chain(*resolved)
    return set(chained)


def _resolve_users_group(value):
    def _by_uid(val):
        user = pwd.getpwuid(int(val))
        return [(user.pw_uid, user.pw_name)]

    def _by_user(val):
        user = pwd.getpwnam(val)
        return [(user.pw_uid, user.pw_name)]

    def _by_gid(val):
        group = grp.getgrgid(int(val))
        return [_by_user(x)[0] for x in group.gr_mem]

    def _by_group(val):
        group = grp.getgrnam(val)
        return [_by_user(x)[0] for x in group.gr_mem]

    if value.startswith('@#'):
        return _by_gid(value[2:])
    if value.startswith('@'):
        return _by_group(value[1:])
    if value.startswith('#'):
        return _by_uid(value[1:])
    return _by_user(value)


@click.command()
@click.option('-n', '--dry-run', is_flag=True, default=True)
@click.option('--soft-limit', callback=to_seconds, default='10m')
@click.option('--hard-limit', callback=to_seconds, default='30m')
@click.option('-k', '--kill', is_flag=True, default=False)
@click.option('-y', '--non-interactive', is_flag=True, default=False)
@click.option('--exclude-user', multiple=True, callback=set_of_users,
              help='Do not touch processes belonging to the specified '
              'user(s). Can be passed multiple times to specify more users. '
              'Specify username, @groupname, #uid or @#gid.')
@click.option('--include-user', multiple=True, callback=set_of_users,
              help='Only touch processes for this user / group. '
              'See --exclude-user for accepted format.')
@click.option('--proc-name', default='sshd',
              help='Filter by process name.')
def main(dry_run, soft_limit, hard_limit, kill, non_interactive,
         exclude_user, include_user, proc_name):

    SOFT_LIMIT = timedelta(seconds=soft_limit)
    HARD_LIMIT = timedelta(seconds=hard_limit)

    def get_uptime_color(uptime):
        if uptime >= HARD_LIMIT:
            return '1'
        if uptime >= SOFT_LIMIT:
            return '3'
        return '2'

    keyval = '\x1b[1m{}:\x1b[0m {}'.format
    click.echo(keyval('Soft limit', SOFT_LIMIT))
    click.echo(keyval('Hard limit', HARD_LIMIT))
    click.echo(keyval('Process name', proc_name))
    click.echo(keyval('Exclude users', ', '.join(x[1] for x in exclude_user)))
    click.echo(keyval('Include users', ', '.join(x[1] for x in include_user)))

    procs = find_processes(
        proc_name,
        exclude_uids=set(x[0] for x in exclude_user),
        include_uids=set(x[0] for x in include_user))

    click.echo(' Found processes '.center(click.get_terminal_size()[0], '='))

    misbehaving = []
    for uptime, proc in sorted(procs):
        if uptime > HARD_LIMIT:
            misbehaving.append(proc)
        print(
            '{pid:6d} '
            '\x1b[36m{name}\x1b[0m '
            '\x1b[1m{user}\x1b[0m '
            '\x1b[1;3{uptime_color}m{uptime}\x1b[0m '
            # 'RUID={uids.real} EUID={uids.effective} SUID={uids.saved}'
            .format(
                pid=proc.pid,
                uptime=uptime,
                uptime_color=get_uptime_color(uptime),
                name=proc.name(),
                user=proc.username(),
                uids=proc.uids()))

    if len(misbehaving) and kill:
        click.echo(' Kill {} processes '
                   .format(len(misbehaving))
                   .center(click.get_terminal_size()[0], '='))

        if (non_interactive or
            click.confirm('Kill {} processes over hard limit?'
                          .format(len(misbehaving)))):

            for proc in misbehaving:
                click.echo(
                    '\x1b[1;31m>\x1b[0m Kill \x1b[36m{}\x1b[0m ... '
                    .format(proc.pid), nl=False)

                try:
                    proc.kill()
                except psutil.NoSuchProcess:
                    click.echo('\x1b[1;33mGONE\x1b[0m')
                else:
                    click.echo('\x1b[1;31mNUKED\x1b[0m')

            click.echo('\n\x1b[1;32m✓\x1b[0m All done.')


if __name__ == '__main__':
    main()
