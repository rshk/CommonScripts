#!/usr/bin/env python

"""
Sets environment variables from a ini file configuration section,
then ``execvpe()`` the passed-in command.
"""

from __future__ import print_function

from ConfigParser import RawConfigParser, NoOptionError
import os
import sys
import textwrap


USAGE = """\
confenv.py <conf-file> <section-name> <command> [<args> ...]

    <conf-file>     Path to INI configuration file
    <section-name>  Name of the INI section to be used
    <command>       Command to be executed
    <args>          Arguments to command
"""


def get_section(cfg, name):
    def _get_section(cfg, name):
        data = {}
        for optname in cfg.options(name):
            data[optname] = cfg.get(name, optname)
        return data

    final_data = {}
    for nm in reversed(get_inheritance(cfg, name)):
        final_data.update(_get_section(cfg, nm))
    final_data.update(_get_section(cfg, name))

    final_data.pop('inherit', None)

    return final_data


def get_inheritance(cfg, section_name):
    deps = []

    def _get_inheritance(cfg, section_name):
        try:
            val = cfg.get(section_name, 'inherit')
        except NoOptionError:
            val = ''
        inheritance = filter(None, (x.strip() for x in val.split(',')))

        _new_items = [x for x in inheritance if x not in deps]
        deps.extend(_new_items)
        for item in _new_items:
            _get_inheritance(cfg, item)

    _get_inheritance(cfg, section_name)
    return deps


def main():
    try:
        file_name = sys.argv[1]
        section_name = sys.argv[2]
        args = sys.argv[3:]
    except IndexError:
        print(USAGE)
        sys.exit(2)

    cfgparser = RawConfigParser()
    cfgparser.optionxform = str
    cfgparser.read(file_name)

    env = get_section(cfgparser, section_name)
    os.execvpe(args[0], args, env)


def test_conf_loading(tmpdir):
    cfg_filename = str(tmpdir.join('myconf.ini'))
    with open(cfg_filename, 'w') as fp:
        fp.write(textwrap.dedent("""
        [trunk]
        SPAM = spam
        EGGS = eggs
        BACON = bacon

        [branch-1]
        inherit = trunk
        SPAM = Spam Spam Spam

        [branch-2]
        inherit = trunk
        EGGS = Eggs!

        [branch-3]
        inherit = trunk
        SPAM = Spam! Spam! Spam!
        BACON = Lovely Bacon

        [leaf]
        inherit = branch-1,branch-2,branch-3
        """))

    cfgparser = RawConfigParser()
    cfgparser.optionxform = str
    cfgparser.read(cfg_filename)

    assert get_inheritance(cfgparser, 'leaf') == [
        'branch-1', 'branch-2', 'branch-3', 'trunk']

    assert get_section(cfgparser, 'trunk') == {
        'SPAM': 'spam',
        'EGGS': 'eggs',
        'BACON': 'bacon',
    }
    assert get_section(cfgparser, 'branch-1') == {
        'SPAM': 'Spam Spam Spam',
        'EGGS': 'eggs',
        'BACON': 'bacon',
    }
    assert get_section(cfgparser, 'leaf') == {
        'SPAM': 'Spam Spam Spam',
        'EGGS': 'Eggs!',
        'BACON': 'Lovely Bacon',
    }


if __name__ == '__main__':
    main()
