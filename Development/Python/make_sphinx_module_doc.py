import argparse
import sys
import os


def _make_page_title(title, underline='#'):
    page_title = '``{}``'.format(title)
    yield page_title + '\n'
    yield underline * (len(page_title)) + '\n\n'


def generate_module_content(module_path):
    module_name = module_path.rsplit('.', 1)[-1]
    yield from _make_page_title(module_name)
    yield '.. automodule:: {}\n'.format(module_path)
    yield '    :members:\n'
    yield '    :undoc-members:\n'


def generate_package_index(package_path):
    package_name = package_path.rsplit('.', 1)[-1]
    yield from _make_page_title(package_name)
    yield '.. toctree::\n'
    yield '    :maxdepth: 2\n'
    yield '    :glob:\n'
    yield '\n'
    yield '    *\n'


def make_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'module_name', metavar='DOTTED_NAME',
        help='Name of the Python module to be documented')
    parser.add_argument(
        '--docs-folder', '-d', default='docs/source', metavar='PATH',
        help='Folder in which documentation modules should be placed')
    parser.add_argument(
        '--no-root-package', action='store_false', default=True,
        help='Remove the "root" package name from generated path')
    return parser


def main():
    parser = make_argument_parser()
    args = parser.parse_args()

    docs_folder = os.path.abspath(args.docs_folder)
    if not os.path.exists(docs_folder):
        raise ValueError(
            'Docs folder not found in {}. '
            'Are you sure you are in the correct directory?'
            .format(docs_folder))

    name_parts = args.module_name.split('.')
    for i in range(1, len(name_parts)):
        path = os.path.join(docs_folder, *name_parts[:i])
        print('Checking', path)
        if not os.path.exists(path):
            print('    > Creating folder', path)
            os.mkdir(path)
        elif not os.path.isdir(path):
            raise ValueError('Not a directory! Aborting')

        index_path = os.path.join(path, 'index.rst')
        if not os.path.exists(index_path):
            print('    > Creating index', index_path)
            with open(index_path, 'wt') as fp:
                fp.writelines(generate_package_index('.'.join(name_parts[:i])))

    module_doc_path = os.path.join(docs_folder, *name_parts) + '.rst'
    print('Checking', module_doc_path)
    if not os.path.exists(module_doc_path):
        print('    > Creating', module_doc_path)
        with open(module_doc_path, 'wt') as fp:
            fp.writelines(generate_module_content('.'.join(name_parts)))
    else:
        print('    !!! Already exists', module_doc_path)
        print('    >>> SKIPPING')


if __name__ == '__main__':
    main()
