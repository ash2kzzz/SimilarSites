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
import getpass
import constants
import timeout_decorator
from git import Repo

linux = "/home/{user}/repo/linux".format(user=getpass.getuser())
repo = Repo(linux)

@timeout_decorator.timeout(20) # 20s
def download(url, id):
    urllib.request.urlretrieve(url, "/tmp/linux-{id}.tar.gz".format(id=id))

class SimilarSitesChecker(object):
    def __init__(self, patch_file, save_flag):
        self.patch_info = patch_parser.PatchInfo(patch_file)
        self.condition_patch_info = None
        self.double_lock_path_info = None
        self.value_use_path_info = None
        self.commit_id = self.patch_info.commit_id
        self.patch_path = self.patch_info.path
        self.save = save_flag
        if self.__fix_check():
            self.__get_source_code()

    def __del__(self):
        self.__release_source_code()

    def __fix_check(self):
        return constants.pattern.search(repo.commit(self.commit_id).message)

    def __get_source_code(self):
        id = self.commit_id
        user = getpass.getuser()
        if not self.commit_id or os.path.exists("/home/{user}/.source/{id}".format(user=user, id=id)):
            return
        os.makedirs("/home/{user}/.source".format(user=user), exist_ok=True)
        url = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/snapshot/linux-{id}.tar.gz".format(id=id)
        try:
            download(url, id)
            os.makedirs("/home/{user}/.source/{id}".format(user=user, id=id))
        except Exception:
            current_path = os.getcwd()
            os.chdir(linux)
            os.makedirs("/home/{user}/.source/{id}/linux-{id}".format(user=user, id=id))
            p = subprocess.Popen("git archive --format=tar.gz --output=\"/tmp/linux-{id}.tar.gz\" {id}".format(id=id), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=-1)
            p.wait()
            os.chdir(current_path)
        tarf = tarfile.open("/tmp/linux-{id}.tar.gz".format(id=id))
        if os.path.exists("/home/{user}/.source/{id}/linux-{id}".format(user=user, id=id)):
            tarf.extractall("/home/{user}/.source/{id}/linux-{id}".format(user=user, id=id))
        else:
            tarf.extractall("/home/{user}/.source/{id}".format(user=user, id=id))
        tarf.close()
        os.remove("/tmp/linux-{id}.tar.gz".format(id=id))
        os.rename("/home/{user}/.source/{id}/linux-{id}".format(user=user, id=id), "/home/{user}/.source/{id}/linux_patched".format(user=user, id=id))
        shutil.copytree("/home/{user}/.source/{id}/linux_patched".format(user=user, id=id), "/home/{user}/.source/{id}/linux_unpatched".format(user=user, id=id), symlinks=True)
        current_path = os.getcwd()
        os.chdir("/home/{user}/.source/{id}/linux_unpatched".format(user=user, id=id))
        subprocess.Popen("patch -REp1 < {patch}".format(patch=self.patch_path), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=-1)
        os.chdir(current_path)

    def __release_source_code(self):
        if not self.commit_id or not os.path.exists("/home/{user}/.source/{id}".format(user=getpass.getuser(), id=self.commit_id)):
            return
        if not self.save:
            shutil.rmtree("/home/{user}/.source/{id}".format(user=getpass.getuser(), id=self.commit_id))

    def __check_rule1_find(self, base_conditions, extra_add_conditions, path, ctx_info):
        for home, _, files in os.walk(os.path.dirname(path)):
            for file in files:
                if file[-2:] != '.c' and file[-2:] != '.h':
                    continue
                with open(home+'/'+file, 'r') as f:
                    next = 0
                    line_list = f.readlines()
                    index = 0
                    while index < len(line_list):
                        if not line_list[index].strip().startswith(r'if (') or common.line_start_with_comment(line_list[index]):
                            index += 1
                            continue
                        if_str = line_list[index].strip()
                        index += 1
                        base = index
                        while not common.complete_if_statement(if_str):
                            if_str += line_list[index].strip()
                            index += 1
                            if index >= len(line_list):
                                next = 1
                                break
                        if next:
                            index += 1
                            break
                        check_conditions = common.get_condition_list(if_str)
                        if not common.the_same_conditions(base_conditions, check_conditions):
                            continue
                        if ctx_info.ctx_type != ctx.statement_ctx_type.unknown:
                            pattern = ctx_info.ctx
                            if not re.compile(pattern).match(line_list[index].strip()):
                                continue
                            index += 1
                        else:
                            if len(base_conditions) <= 1:
                                continue
                        for condition in extra_add_conditions:
                            if condition not in check_conditions:
                                error_path = str(home) + '/' + str(file)
                                error_path = error_path.split("/linux_patched/")[1]
                                print('[*] {path}:{line} miss condition \"{message}\".'.format(path=error_path, line=base, message=condition))
    
    def check_rule1(self):
        if not self.commit_id:
            return
        self.condition_patch_info = patch_parser.ConditionPatchInfo(self.patch_path)
        multi_list = self.condition_patch_info.get_multi_res_conditions()
        if not multi_list:
            return
        for base_conditions, extra_add_conditions, sub_path, ctx_info in multi_list:
            if len(base_conditions) == 0 or len(extra_add_conditions) == 0:
                continue
            self.__check_rule1_find(base_conditions, extra_add_conditions, os.path.join("/home/{user}/.source/{id}/linux_patched".format(user=getpass.getuser(), id=self.commit_id), sub_path) ,ctx_info)

    def __check_rule2_find(self, path, ctx_info):
        with open(path, 'r') as f:
            line_list = f.readlines()
            index = 0
            while index < len(line_list):
                base = index + 1
                if not common.function_in_line(line_list[index], ctx_info.func_name_list) or common.line_start_with_comment(line_list[index]):
                    index += 1
                    continue
                # print(line_list[index].strip())
                # print(ctx_info.func_name_list)
                # index += 1
                # continue
                if common.search_forward_lock(line_list, index-1, ctx_info.ctx_type, ctx_info.ctx_args) and common.search_backward_unlock(line_list, index+1, ctx_info.ctx_type, ctx_info.ctx_args):
                    index = common.search_backward_unlock(line_list, index+1, ctx_info.ctx_type, ctx_info.ctx_args) + 1
                    continue
                else:
                    error_path = path.split("/linux_patched/")[1]
                    print('[*] {path}:{line} miss locks \"{message}\".'.format(path=error_path, line=base, message=common.lock_type_to_str(ctx_info.ctx_type)))
                    index += 1
                                    
    def check_rule2(self):
        if not self.commit_id:
            return
        self.double_lock_path_info = patch_parser.DoubleLockPatchInfo(self.patch_path)
        res_list = self.double_lock_path_info.get_res_locks()
        if not res_list:
            return
        # for path, ctx_info in res_list:
        #     print("path:{path}\nlock args:{args}\nfunc:{name}".format(path=path, args=ctx_info.ctx_args, name=ctx_info.func_name_list))
        # return
        for sub_path, ctx_info in res_list:
            self.__check_rule2_find(os.path.join("/home/{user}/.source/{id}/linux_patched".format(user=getpass.getuser(), id=self.commit_id), sub_path), ctx_info)

    def __check_rule3_find(self, d, macro_d, path_list, changed_lines):
        checked_macro = copy.deepcopy(macro_d)
        for variable, new_variable in d.items():
            macro = ''
            if variable in macro_d:
                macro = macro_d[variable]
                if variable in checked_macro:
                    del checked_macro[variable]
            for sub_path in path_list:
                path = os.path.join("/home/{user}/.source/{id}/linux_patched".format(user=getpass.getuser(), id=self.commit_id), sub_path)
                if not os.path.exists(path):
                    continue
                with open(path, 'r') as f:
                    line_list = f.readlines()
                    index = 0
                    while index < len(line_list):
                        recheck = 0
                        base = index + 1
                        if not re.compile('[\W]'+common.add_escape(str(variable))+'[\W]').search(line_list[index]) or common.line_start_with_comment(line_list[index]):
                            index += 1
                            continue
                        for already_new_variable in d.values():
                            if already_new_variable in line_list[index]:
                                recheck = 1
                                break
                        if recheck or common.is_debug_statement(line_list[index]) or base in changed_lines[sub_path]:
                            index += 1
                            continue
                        if len(macro):
                            pattern = macro + '(' + variable
                            if pattern in line_list[index]:
                                index += 1
                                continue
                            else:
                                print('[*] {path}:{line} Variable \"{message1}\" needs to be changed to \"{message2}\", or add a macro \"{message3}\".'.format(path=sub_path, line=base, message1=variable, message2=new_variable, message3=macro))
                                index += 1
                                continue
                        print('[*] {path}:{line} Variable \"{message1}\" needs to be changed to \"{message2}\".'.format(path=sub_path, line=base, message1=variable, message2=new_variable))
                        index += 1
        for variable, macro in checked_macro.items():
            for sub_path in path_list:
                path = os.path.join("/home/{user}/.source/{id}/linux_patched".format(user=getpass.getuser(), id=self.commit_id), sub_path)
                if not os.path.exists(path):
                    continue
                with open(path, 'r') as f:
                    line_list = f.readlines()
                    index = 0
                    while index < len(line_list):
                        base = index + 1
                        if variable not in line_list[index] or base in changed_lines[sub_path]:
                            index += 1
                            continue
                        pattern = macro + '(' + variable
                        if pattern not in line_list[index]:
                            print('[*] {path}:{line} Variable \"{message1}\" needs to add a macro \"{message2}\".'.format(path=sub_path, line=base, message1=variable, message2=macro))
                        index += 1

    def check_rule3(self):
        if not self.commit_id:
            return
        self.value_use_path_info = patch_parser.ValueUsePatchInfo(self.patch_path)
        changed_d = self.value_use_path_info.get_variable_change()
        add_macro_d = self.value_use_path_info.get_variable_add_macro()
        path_list = self.value_use_path_info.get_all_file_path()
        changed_lines_d = self.value_use_path_info.get_changed_lines()
        if not (len(changed_d) + len(add_macro_d)):
            return
        # print("changed:{change}   add macro:{add}".format(change=changed_d, add=add_macro_d))
        # return
        self.__check_rule3_find(changed_d, add_macro_d, path_list, changed_lines_d)

    def check_all(self):
        if self.__fix_check():
            self.check_rule1()
            self.check_rule2()
            self.check_rule3()
        
