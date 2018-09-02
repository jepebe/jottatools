#!/usr/bin/env python

from pathlib2 import Path
import argparse


def no_filter(item):
    return True


def relative(basedir, path):
    return path.relative_to(basedir)


def visit(basedir, folder, remote=None, filter=no_filter, dry=False):
    cur = basedir / folder

    items = [item for item in cur.iterdir() if filter(basedir, item)]
    for item in items:
        if item.is_dir():
            visit(basedir, item, remote, filter, dry)
        else:
            if dry:
                print("File: %s" % relative(basedir, item))
            else:
                src = relative(basedir, item)
                if remote is None:
                    print('jotta-cli archive \'%s\'' % src)
                else:
                    print('jotta-cli archive \'%s\' --remote %s' % (src, remote))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('folder', action='store',
                        help='Folder to archive from')

    parser.add_argument('-r', '--remote-dir', action='store', dest='remote',
                        default=None,
                        help='Destination directory')

    parser.add_argument('-i', action='store_true', dest='include_hidden',
                        help='Include hidden files')

    parser.add_argument('--dry_run', action='store_true', dest='dry',
                        help='Do a dry run. Only print paths')

    parser.add_argument('-e', '--exclude', nargs='+', dest='exclude',
                        help='List of items to exclude')

    args = parser.parse_args()
    basedir = Path(args.folder).resolve()

    def filter(basedir, item):
        excluded = args.exclude if args.exclude is not None else []
        if any([item.match(pattern) for pattern in excluded]):
            print('Excl: %s' % relative(basedir, item))
            return False
        if not args.include_hidden and item.name.startswith('.'):
            print('Hide: %s' % relative(basedir, item))
            return False
        return True

    remote = Path(args.remote) if args.remote is not None else None
    visit(basedir, Path('.'), remote, filter, dry=args.dry)
