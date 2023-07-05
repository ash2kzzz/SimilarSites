#!/usr/bin/env python3

import checker
import argparse
import getpass
import re
from git import Repo

linux = '/home/' + getpass.getuser() + "/repo/linux"
pattern = re.compile(r'Fixes:[ ]?(commit )?([0-9a-fA-F]{12,})')

if __name__ == '__main__':
    repo = Repo(linux)
    
    arg_parser = argparse.ArgumentParser(description='Output some necessary information after parsing.', add_help=True)
    arg_parser.add_argument("-p", "--path", type=str, help="The absolute path where the patch is located.")
    
    args = arg_parser.parse_args()

    if not args.path:
        raise Exception('no input')

    c = checker.SimilarSitesChecker(args.path)
    commit = repo.commit(c.patch_info.commit_id)
    if pattern.search(commit.message):
        c.check_rule1()
        c.check_rule2()
        c.check_rule3()
        print(str(c.patch_info.commit_id) + ' is finished.')
    else:
        print(str(c.patch_info.commit_id) + ' is not Fixes Tag patch.')

