#!/usr/bin/env python

# autobuild.py - Generic autobuilder script for Linux.
#
# Waits for changes in a given directory, then runs
# a command (usually, to rebuild something).
#
# (C) 2012-2016 Samuele Santi - Under BSD 2-clause License
#
# Install requirements:
#
#   pip install inotify

import argparse
import os
import re
import subprocess
import sys
from fnmatch import fnmatch

import inotify.adapters
from inotify.constants import (
    IN_CLOSE_WRITE, IN_CREATE, IN_DELETE, IN_MODIFY, IN_MOVE, IN_MOVE_SELF,
    IN_MOVED_FROM, IN_MOVED_TO)

enable_notifications = False
default_mask = (IN_CLOSE_WRITE | IN_CREATE | IN_DELETE | IN_MODIFY |
                IN_MOVE | IN_MOVED_FROM | IN_MOVED_TO | IN_MOVE_SELF)

default_exclude_re = re.compile(rb'^(.*~|\.#.*|#.*#)$')


def quote_command(command):
    def _needs_quoting(part):
        return not re.match(r'^[a-zA-Z0-9_./=@%-]+$', part)

    def _quote_iter(part):
        yield '"'
        for letter in part:
            if letter == '"':
                yield '\\"'
            else:
                yield letter
        yield '"'

    def _quote(part):
        return ''.join(_quote_iter(part))

    return ' '.join(_quote(x) if _needs_quoting(x) else x for x in command)


def msg(text, color='0'):
    col_open = '\x1b[{}m'.format(color)
    col_close = '\x1b[0m'
    print('{}{}{}'.format(col_open, text, col_close))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-w', '--workdir', dest='workdir',
        help='Specify the working directory in which to execute the command. '
        '(Defaults to the current directory)')
    parser.add_argument(
        '-l', '--listen', action='append', dest='listen_paths', default=[],
        help='Add a directory to the watch list')
    parser.add_argument(
        '-e', '--exclude', action='append', dest='exclude_paths', default=[],
        help='Exclude files matching this (glob) pattern')
    parser.add_argument(
        '-n', '--notify', action='store_true', dest='notify', default=False,
        help='Send notifications about the command exit status')
    parser.add_argument(
        'command', nargs=argparse.REMAINDER,
        help='Command to be executed upon events')

    return parser.parse_args()


def name_match(name, exclude_paths):
    if default_exclude_re.match(name):
        return False

    exclude_patterns = (x.encode() for x in exclude_paths)
    for pattern in exclude_patterns:
        if fnmatch(name, pattern):
            return False
    return True


class InotifyTrees(inotify.adapters.BaseTree):

    # FORKED TO FIX UNICODE BUG IN __load_trees()

    def __init__(self, paths, mask=inotify.constants.IN_ALL_EVENTS,
                 block_duration_s=inotify.adapters._DEFAULT_EPOLL_BLOCK_DURATION_S):  # noqa
        super().__init__(mask=mask, block_duration_s=block_duration_s)
        self.__load_trees(paths)

    def __load_trees(self, paths):
        q = paths
        while q:
            current_path = q[0]
            del q[0]

            self._i.add_watch(current_path, self._mask)

            for filename in os.listdir(current_path):
                entry_filepath = os.path.join(current_path, filename)
                if os.path.isdir(entry_filepath) is False:
                    continue

                q.append(entry_filepath)


def watch_events(listen_paths, exclude_paths):
    listen_paths = [x.encode() for x in listen_paths]
    watcher = InotifyTrees(listen_paths)
    for event in watcher.event_gen():
        if event is None:
            continue  # hmm...
        # msg(event, color='2')
        header, _, _, filename = event
        if not header.mask & default_mask:
            continue
        if name_match(filename, exclude_paths):
            yield event


def check_notify_send():
    return not subprocess.call(('which', 'notify-send'))


def send_notification(title, description, icon, urgency='normal',
                      timeout=2000):
    subprocess.call([
        'notify-send', title, description,
        '--icon', icon,
        '--urgency', urgency,
        '--expire-time', str(timeout)])


def run_command(command, **kwargs):
    cmd_repr = quote_command(command)
    msg('Running command: {}'.format(cmd_repr), '34')
    retval = subprocess.call(command, **kwargs)

    if not retval:
        msg('Command execution successful', '32')
    else:
        msg('Command execution failed with code {}'.format(retval), '31')

    if enable_notifications:
        if retval == 0:  # success
            icon = 'dialog-information'
            title = "Command execution successful"
            urgency = 'normal'
            timeout = 2000

        else:
            icon = "dialog-error"
            title = "Command execution failed (code: {})".format(retval)
            urgency = 'critical'
            timeout = 5000

        description = (
            '{command}\n\n'
            'Workdir: {workdir}\n'
            .format(command=cmd_repr,
                    workdir=str(kwargs.get('cwd', os.getcwd()))))

        send_notification(
            title, description, icon=icon, urgency=urgency, timeout=timeout)


def main():
    global enable_notifications

    args = parse_args()
    workdir = args.workdir or os.getcwd()
    if not len(args.listen_paths):
        msg('At least one listen path is required', color='31')
        sys.exit(1)

    enable_notifications = args.notify
    if enable_notifications and (not check_notify_send()):
        msg('Program notify-send not found. Disabling notifications.', '33')
        enable_notifications = False

    for path in args.listen_paths:
        print('Listening on: {}'.format(path))
    print('Will run: {}'.format(quote_command(args.command)))
    print('-' * 60)

    for event in watch_events(args.listen_paths, args.exclude_paths):
        hdr, names, path, filename = event
        msg('{} {}'
            .format(', '.join(names),
                    os.path.join(path, filename).decode()),
            color='2')
        run_command(args.command, cwd=workdir)


if __name__ == '__main__':
    main()
