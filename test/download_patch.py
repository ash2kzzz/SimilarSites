#!/usr/bin/env python3

import urllib.request
import sys

name = 'ground_truth'
#name = 'next_data'
#name = 'test'
file = './{n}.txt'.format(n=name)
folder = '../{n}_patch/'.format(n=name)

if __name__ == '__main__':    
    with open(file, 'r') as f:
        for commit_id in f.readlines():
            commit_id = commit_id.strip('\n')
            if len(commit_id) == 0:
                continue
            url = 'https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/patch/?id=' + str(commit_id)
            urllib.request.urlretrieve(url, folder + str(commit_id) + '.patch')
    sys.exit()