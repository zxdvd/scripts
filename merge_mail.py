#! /usr/bin/python3
# coding=utf-8

import os
import argparse
import hashlib
from shutil import copy2

def create_md5(dir):
    '''Create a file to store all md5sum of a folder, need to give a
    specific folder.
    '''
    with open('file.md5','w') as record:
        for path, dirs, files in os.walk(dir):
            for name in files:
                full_path = os.path.join(path, name)
                with open(full_path, 'rb') as f:
                    md5 = hashlib.md5(f.read()).hexdigest()
                print(full_path+':'+md5, file=record)

def merge_dir(dir, merge_dir):
    '''Merge two folder. For every file in import_dir, calc its md5sum.
    If it is contained in the md5sum file, skip it. If not, copy it.
    '''
    try:
        with open('file.md5','r') as md5file:
            s = md5file.read()
            for path, dirs, files in os.walk(merge_dir):
                for name in files:
                    full_path = os.path.join(path, name)
                    with open(full_path, 'rb') as f:
                        md5 = hashlib.md5(f.read()).hexdigest()
                        if md5 not in s:
                            dst = full_path.replace(merge_dir, dir)
                            print(dst)
                            try:
                                copy2(full_path, dst)
                            except Error as e:
                                print("{}".format(e))
                            create_md5(dir)
    except IOError as e:
        print("({})".format(e))

def main():
    parser = argparse.ArgumentParser(description='merge mail')
    parser.add_argument('-c', '--create',
                        help='create a file to store all md5sum',
                        action="store_true")
    parser.add_argument('-d', '--dir',
                        help='the target folder need to create md5sum')
    parser.add_argument('-m', '--merge',
                        help='merge mail from another dir, check md5 of'
                             + ' that file to avoid duplicate ')

    args = parser.parse_args()

    if args.dir:
        print(args.dir)
        if args.create:
            create_md5(args.dir)
        if args.merge:
            merge_dir(args.dir, args.merge)


if __name__ == "__main__":
    main()
