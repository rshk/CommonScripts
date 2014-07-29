#!/usr/bin/env python

import crypt
import getpass
import random
import string
import sys


def gen_salt():
    pool = string.ascii_letters + string.digits + './'
    return ''.join(random.choice(pool) for x in xrange(8))  # MUST be 8 bytes


if len(sys.argv) > 1:
    password = sys.argv[1]
else:
    password = getpass.getpass(prompt="Password: ")
    password2 = getpass.getpass(prompt="Password (again): ")

    if password != password2:
        print("Mismatching password! (Aborting)")
        sys.exit(1)


if len(sys.argv) > 2:
    amount = int(sys.argv[2])
else:
    amount = 1

for x in xrange(amount):
    hashed = crypt.crypt(password, '$6$' + gen_salt())
    print(hashed)
