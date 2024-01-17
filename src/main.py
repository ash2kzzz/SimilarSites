#!/usr/bin/env python3

import checker
import argparse

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Output some necessary information before parsing.', add_help=True)
    arg_parser.add_argument("-p", "--path", type=str, help="The absolute path where the patch is located.")
    arg_parser.add_argument("-s", "--save", type=bool, help="Whether to save the source code locally. (defualt = False)")
    
    args = arg_parser.parse_args()

    if not args.path:
        raise Exception('no input')
    if not args.save:
        args.save = False

    c = checker.SimilarSitesChecker(args.path, args.save)
    c.check_all()
    print('{commit_id} is finished.'.format(commit_id=c.commit_id))

