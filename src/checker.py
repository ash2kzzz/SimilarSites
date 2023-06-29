#!/usr/bin/env python3

import common
import patch_parser
import ctx
import os
import re
import tarfile
import shutil
import copy
# import linecache
import urllib.request
import subprocess

class SimilarSitesChecker(object):
    def __init__(self, patch_file):
        self.patch_info = patch_parser.PatchInfo(patch_file)
        self.condition_patch_info = None
        self.double_lock_path_info = None
        self.value_use_path_info = None
        self.commit_id = self.patch_info.commit_id
        self.patch_path = self.patch_info.path
        self.__get_source_code()

    def __del__(self):
        self.__release_source_code()

    def __get_source_code(self):
        if not self.commit_id or os.path.exists('/tmp/'+str(self.commit_id)):
            return
        os.makedirs('/tmp/'+str(self.commit_id))
        url = 'https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/snapshot/linux-'+str(self.commit_id)+'.tar.gz'
        urllib.request.urlretrieve(url, '/tmp/'+str(self.commit_id)+'/linux-'+str(self.commit_id)+'.tar.gz')
        tarf = tarfile.open('/tmp/'+str(self.commit_id)+'/linux-'+str(self.commit_id)+'.tar.gz')
        tarf.extractall('/tmp/'+str(self.commit_id))
        tarf.close()
        os.remove('/tmp/'+str(self.commit_id)+'/linux-'+str(self.commit_id)+'.tar.gz')
        os.rename('/tmp/'+str(self.commit_id)+'/linux-'+str(self.commit_id), '/tmp/'+str(self.commit_id)+'/linux_patched')
        shutil.copytree('/tmp/'+str(self.commit_id)+'/linux_patched', '/tmp/'+str(self.commit_id)+'/linux_unpatched')
        current_path = os.getcwd()
        os.chdir('/tmp/'+str(self.commit_id)+'/linux_unpatched')
        subprocess.Popen('patch -REp1'+' < '+str(self.patch_path), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=-1)
        os.chdir(current_path)

    def __release_source_code(self):
        if not self.commit_id or not os.path.exists('/tmp/'+str(self.commit_id)):
            return
        shutil.rmtree('/tmp/'+str(self.commit_id))

    def __check_rule1_find(self, judge_conditions, change_conditions, path, ctx_info):
        for home, _, files in os.walk(os.path.dirname(path)):
            for file in files:
                if file[-2:] != '.c' and file[-2:] != '.h':
                    continue
                with open(home+'/'+file, 'r') as f:
                    next = 0
                    line_list = f.readlines()
                    index = 0
                    while index < len(line_list):
                        recheck = 0
                        if not line_list[index].strip().startswith(r'if ('):
                            index += 1
                            continue
                        base = index + 1
                        if_str = line_list[index].strip()
                        index += 1
                        while not common.complete_if_statement(if_str):
                            if_str += line_list[index].strip()
                            index += 1
                            if index >= len(line_list):
                                next = 1
                                break
                        if next:
                            break
                        check_conditions = common.get_condition_list(if_str)
                        for condition in judge_conditions:
                            if condition not in check_conditions:
                                recheck = 1
                                break
                        if recheck:
                            continue
                        if ctx_info.ctx_type != ctx.statement_ctx_type.unknown:
                            pattern = ctx_info.ctx
                            if not re.compile(pattern).match(line_list[index].strip()):
                                continue
                            index += 1
                        else:
                            # unknown
                            continue
                        for condition in change_conditions:
                            if condition not in check_conditions:
                                error_path = str(home) + '/' + str(file)
                                error_path = error_path[60:]
                                print('[*] ' + str(error_path) + ':' + str(base) + ' miss condition \"' + condition + '\".')
                                print(self.commit_id)
    
    def check_rule1(self):
        if not self.commit_id:
            return
        self.condition_patch_info = patch_parser.ConditionPatchInfo(self.patch_path)
        multi_list = self.condition_patch_info.get_multi_res_conditions()
        if not multi_list:
            return
        for judge_conditions, change_conditions, sub_path, ctx_info in multi_list:
            if len(judge_conditions) == 0 or len(change_conditions) == 0:
                continue
            self.__check_rule1_find(judge_conditions, change_conditions, os.path.join('/tmp/'+str(self.commit_id)+'/linux_patched/', sub_path) ,ctx_info)

    def __check_rule2_find(self, path, ctx_info):
        with open(path, 'r') as f:
            line_list = f.readlines()
            index = 0
            while index < len(line_list):
                base = index + 1
                if common.capture_function_call(line_list[index]) not in ctx_info.func_name_list:
                    index += 1
                    continue
                if common.search_forward_lock(line_list, index-1, ctx_info.ctx_type) and common.search_backward_unlock(line_list, index+1, ctx_info.ctx_type):
                    index = common.search_backward_unlock(line_list, index+1, ctx_info.ctx_type) + 1
                    continue
                else:
                    error_path = path
                    error_path = error_path[60:]
                    print('[*] ' + str(error_path) + ':' + str(base) + ' miss locks \"' + common.lock_type_to_str(ctx_info.ctx_type) + '\".')
                    print(self.commit_id)
                    index += 1
                                    
    def check_rule2(self):
        if not self.commit_id:
            return
        self.double_lock_path_info = patch_parser.DoubleLockPatchInfo(self.patch_path)
        res_list = self.double_lock_path_info.get_res_locks()
        if not res_list:
            return
        for sub_path, ctx_info in res_list:
            self.__check_rule2_find(os.path.join('/tmp/'+str(self.commit_id)+'/linux_patched/', sub_path), ctx_info)

    def __check_rule3_find(self, d, macro_d, path_list):
        checked_macro = copy.deepcopy(macro_d)
        for variable, new_variable in d.items():
            macro = ''
            if variable in macro_d:
                macro = macro_d[variable]
                if variable in checked_macro:
                    del checked_macro[variable]
            for sub_path in path_list:
                path = os.path.join('/tmp/'+str(self.commit_id)+'/linux_patched/', sub_path)
                if not os.path.exists(path):
                    continue
                with open(path, 'r') as f:
                    line_list = f.readlines()
                    index = 0
                    while index < len(line_list):
                        recheck = 0
                        base = index + 1
                        if variable not in line_list[index]:
                            index += 1
                            continue
                        for already_new_variable in d.values():
                            if already_new_variable in line_list[index]:
                                recheck = 1
                                break
                        if recheck or line_list[index].strip().startswith(r'pr_debug'):
                            index += 1
                            continue
                        if len(macro):
                            pattern = macro + '(' + variable
                            if pattern in line_list[index]:
                                index += 1
                                continue
                            else:
                                print('[*] ' + str(sub_path) + ':' + str(base) + ' Variable \"' + str(variable) + '\" needs to be changed to \"' + str(new_variable) + '\", or add a macro \"' + str(macro) + '\".')
                                print(self.commit_id)
                                index += 1
                                continue
                        print('[*] ' + str(sub_path) + ':' + str(base) + ' Variable \"' + str(variable) + '\" needs to be changed to \"' + str(new_variable) + '\".')
                        print(self.commit_id)
                        index += 1
        for variable, macro in checked_macro.items():
            for sub_path in path_list:
                path = os.path.join('/tmp/'+str(self.commit_id)+'/linux_patched/', sub_path)
                if not os.path.exists(path):
                    continue
                with open(path, 'r') as f:
                    line_list = f.readlines()
                    index = 0
                    while index < len(line_list):
                        base = index + 1
                        if variable not in line_list[index]:
                            index += 1
                            continue
                        pattern = macro + '(' + variable
                        if pattern not in line_list[index]:
                            print('[*] ' + str(sub_path) + ':' + str(base) + ' Variable \"' + str(variable) + '\" needs to add a macro \"' + str(macro) + '\".')
                            print(self.commit_id)
                        index += 1

    def check_rule3(self):
        if not self.commit_id:
            return
        self.value_use_path_info = patch_parser.ValueUsePatchInfo(self.patch_path)
        changed_d = self.value_use_path_info.get_variable_change()
        add_macro_d = self.value_use_path_info.get_variable_add_macro()
        if not (len(changed_d) + len(add_macro_d)):
            return
        self.__check_rule3_find(changed_d, add_macro_d, self.value_use_path_info.get_all_file_path())

