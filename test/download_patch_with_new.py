#!/usr/bin/env python3

import urllib.request
import os

if __name__ == '__main__':
    with open('./new.txt', 'r') as f:
        for commit_id in f.readlines():
            commit_id = commit_id.strip('\n')
            if len(commit_id) == 0:
                continue
            url = 'https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/patch/?id=' + str(commit_id)
            urllib.request.urlretrieve(url, '../new_patch/' + str(commit_id) + '.patch')