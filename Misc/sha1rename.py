import sys
import os
import hashlib


def rename_file(name):
    dirname = os.path.dirname(name)
    _, ext = os.path.splitext(name)

    with open(name, 'rb') as fp:
        file_hash = hashlib.sha1(fp.read()).hexdigest()
    new_name = os.path.join(dirname, '{}{}'.format(file_hash, ext))

    print('{} -> {}'.format(name, new_name))
    if os.path.exists(new_name):
        print('    Destination exists, skipping')
    else:
        os.rename(name, new_name)


if __name__ == '__main__':
    for arg in sys.argv[1:]:
        rename_file(arg)
