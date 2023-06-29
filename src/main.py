#!/usr/bin/env python3

import checker
import argparse

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Output some necessary information after parsing.', add_help=True)
    arg_parser.add_argument("-p", "--path", type=str, help="The absolute path where the patch is located.")
    
    args = arg_parser.parse_args()

    if not args.path:
        raise Exception('no input')

    c = checker.SimilarSitesChecker(args.path)
    c.check_rule1()
    c.check_rule2()
    c.check_rule3()