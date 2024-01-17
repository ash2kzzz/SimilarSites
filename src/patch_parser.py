#!/usr/bin/env python3

import constants
import os
import common
import ctx
import operator
from unidiff import PatchSet

class PatchInfo(object):
    """
    self.path: the path of the patch file
    self.commit_id: the commit id of the patch
    """
    def __init__(self, path):
        self.path = os.path.abspath(path)
        #with open(self.path, 'r') as f:
        #    m = constants.COMMIT_ID.match(f.readline().strip('\n'))
        #    if m:
        #        self.commit_id = m.group(1)
        #    else:
        #        self.commit_id = None
        m = constants.PATH_COMMIT_ID.match(self.path) # get commit ID from filename (eg. 1596dae2f17ec5c6e8c8f0e3fec78c5ae55c1e0b.patch)
        if m:
            self.commit_id = m.group(2)
        else:
            self.commit_id = None
    
class ConditionPatchInfo(PatchInfo):
    def __init__(self, patch_file):
        super(ConditionPatchInfo, self).__init__(patch_file)
        self.patch = PatchSet.from_filename(self.path, encoding='utf-8')
        self.multi_res = []
        self.__parser_patch()

    def __parser_patch(self):
        for file in self.patch:
            for hunk in file:
                index = 0
                while index < len(hunk):
                    # scan the beginning of a removed-if-statement 
                    if hunk[index].is_removed and hunk[index].value.strip().startswith(r'if ('):
                        remove_str = hunk[index].value.strip()
                        index += 1
                        if (index >= len(hunk)):
                            break
                        back = index
                        # get the removed-if-statement
                        while index < len(hunk) and hunk[index].is_removed and not common.complete_if_statement(remove_str):
                            remove_str += hunk[index].value.strip()
                            index += 1
                        if (index >= len(hunk)):
                            break
                        # hold the removed-if-statement
                        if not hunk[index].is_added or not hunk[index].value.strip().startswith(r'if ('):   # just remove the condition or not added-if-statement
                            continue
                        if not common.complete_if_statement(remove_str):   # the removed-if-statement is not complete
                            add_str = hunk[index].value.strip()
                            index += 1
                            if (index >= len(hunk)):
                                break
                            while index < len(hunk) and hunk[index].is_added:
                                add_str += hunk[index].value.strip()
                                index += 1
                            if (index >= len(hunk)):
                                break
                            while index < len(hunk) and common.complete_if_statement(remove_str):
                                remove_str += hunk[index].value.strip()
                                add_str += hunk[index].value.strip()
                                index += 1
                        else:
                            add_str = hunk[index].value.strip()
                            index += 1
                            if (index >= len(hunk)):
                                break
                            while index < len(hunk) and hunk[index].is_added and not common.complete_if_statement(add_str):
                                add_str += hunk[index].value.strip()
                                index += 1
                        if (index >= len(hunk)):
                            break
                        ctx_info = ctx.StatementCTXInfo(hunk[index].value.strip())
                        if not common.complete_if_statement(remove_str) or not common.complete_if_statement(add_str):
                            index = back
                            continue
                        remove_conditions = common.get_condition_list(remove_str)
                        add_conditions = common.get_condition_list(add_str)
                        base_conditions = common.get_base_conditions(remove_conditions, add_conditions)
                        remove_base_conditions = common.get_remove_base_conditions(remove_conditions)
                        if not common.the_same_conditions(base_conditions, remove_base_conditions):   # keep the base conditions is all
                            index = back
                            continue
                        extra_add_conditions = common.get_extra_add_conditions(remove_conditions, add_conditions)
                        self.multi_res.append((base_conditions, extra_add_conditions, file.path, ctx_info))
                        remove_conditions2 = common.reverse_condition_list(remove_conditions)
                        add_conditions2 = common.reverse_condition_list(add_conditions)
                        base_conditions2 = common.get_base_conditions(remove_conditions2, add_conditions2)
                        extra_add_conditions2 = common.get_extra_add_conditions(remove_conditions2, add_conditions2)
                        self.multi_res.append((base_conditions2, extra_add_conditions2, file.path, ctx_info))
                    else:
                        index += 1
                        continue

    def get_multi_res_conditions(self):
        if len(self.multi_res):
            return self.multi_res
        else:
            return None

class DoubleLockPatchInfo(PatchInfo):
    def __init__(self, patch_file):
        super(DoubleLockPatchInfo, self).__init__(patch_file)
        self.patch = PatchSet.from_filename(self.path, encoding='utf-8')
        self.res = []
        self.__parser_patch()

    def __parser_patch(self):
        for file in self.patch:
            for hunk in file:
                index = 0
                while index < len(hunk):
                    if hunk[index].is_added and common.is_lock_statement(hunk[index].value):
                        lock_type = common.statement_lock_type(hunk[index].value)
                        lock_args = common.statement_lock_args(hunk[index].value)
                        func_list = [] # (func_name, func_args_list)
                        index += 1
                        base = index
                        if (index >= len(hunk)):
                            break
                        while index < len(hunk) and hunk[index].is_context and not common.end_of_function(hunk[index].value) and not common.is_unlock_statement(hunk[index].value):
                            if common.capture_function_call(hunk[index].value):
                                func_list.append((common.capture_function_call(hunk[index].value), common.capture_function_args(hunk[index].value)))
                            index += 1
                        if (index >= len(hunk)):
                            break
                        if common.end_of_function(hunk[index].value):
                            index = base
                            continue
                        if hunk[index].is_added and not common.is_unlock_statement(hunk[index].value):
                            continue
                        # print("CTX: lock type:{type}  lock args:{args}".format(type=common.lock_type_to_str(lock_type), args=lock_args))
                        # print("LINE: lock type:{type}  lock args:{args}".format(type=common.lock_type_to_str(common.statement_unlock_type(hunk[index].value)), args=common.statement_lock_args(hunk[index].value)))
                        if hunk[index].is_removed or common.statement_unlock_type(hunk[index].value) != lock_type or common.statement_lock_args(hunk[index].value) != lock_args or len(func_list) == 0:
                            index += 1
                            continue
                        ctx_info = ctx.LockCTXInfo(func_list, lock_type, lock_args)
                        if not self.already_have_it(ctx_info):
                            self.res.append((file.path, ctx_info))
                    else:
                        index += 1
                        continue
                    
    def get_res_locks(self):
        if len(self.res):
            return self.res
        else:
            return None
        
    def already_have_it(self, ctx_info):
        for _, already_ctx_info in self.res:
            if already_ctx_info.ctx_type != ctx_info.ctx_type:
                continue
            if len(already_ctx_info.func_name_list) != len(ctx_info.func_name_list):
                continue
            check_len_list = []
            for func_tuple in already_ctx_info.func_name_list:
                for func_tuple2 in ctx_info.func_name_list:
                    if operator.eq(func_tuple, func_tuple2):
                        check_len_list.append(func_tuple2)
            if len(check_len_list) == len(ctx_info.func_name_list):
                return True
        return False

class ValueUsePatchInfo(PatchInfo):
    def __init__(self, patch_file):
        super(ValueUsePatchInfo, self).__init__(patch_file)
        self.patch = PatchSet.from_filename(self.path, encoding='utf-8')
        self.d = {}
        self.d_macro = {}
        self.path = []
        self.__parser_patch()

    def __parser_patch(self):
        for file in self.patch:
            self.path.append(file.path)
            for hunk in file:
                index = 0
                while index < len(hunk):
                    if hunk[index].is_removed:
                        if common.is_assign_statement(hunk[index].value.strip()):
                            left_value, right_value = common.assign_statement_get_value(hunk[index].value.strip())
                            index += 1
                            if hunk[index].is_added and common.is_assign_statement(hunk[index].value.strip()):
                                next_left, next_right = common.assign_statement_get_value(hunk[index].value.strip())
                                index += 1
                                if next_left != left_value:
                                    continue
                                self.__add_d(right_value, next_right)
                            elif hunk[index].is_added and common.macro_statement_get_value(hunk[index].value.strip()):
                                next_left, next_right = common.macro_statement_get_value(hunk[index].value.strip())
                                index += 1
                                if next_left != left_value:
                                    continue
                                self.__add_d_macro(next_left, common.macro_statement_get_macro(hunk[index-1].value.strip()))
                            else:
                                continue
                        elif common.is_compare_statement(hunk[index].value.strip()):
                            left_value, right_value = common.compare_statement_get_value(hunk[index].value.strip())
                            index += 1
                            if hunk[index].is_removed and common.is_assign_statement(hunk[index].value.strip()):
                                next_left, next_right = common.assign_statement_get_value(hunk[index].value.strip())
                                index += 1
                                if not hunk[index].is_added or not common.is_compare_statement(hunk[index].value.strip()):
                                    continue
                                left_value_add, right_value_add = common.compare_statement_get_value(hunk[index].value.strip())
                                self.__add_d(left_value, left_value_add)
                                self.__add_d(right_value, right_value_add)
                                index += 1
                                if not hunk[index].is_added:
                                    continue
                                if common.is_assign_statement(hunk[index].value.strip()):
                                    left_value_a, right_value_a = common.assign_statement_get_value(hunk[index].value.strip())
                                    index += 1
                                    if left_value != left_value_a:
                                        continue
                                    self.__add_d(right_value, right_value_a)
                                elif common.is_macro_statement(hunk[index].value.strip()):
                                    left_value_a, right_value_a = common.macro_statement_get_value(hunk[index].value.strip())
                                    self.__add_d_macro(left_value_a, common.macro_statement_get_macro(hunk[index].value.strip()))
                                    index += 1
                                else:
                                    continue
                            else:
                                continue
                        else:
                            index += 1
                    else:
                        index += 1

    def __add_d(self, value, value_add):
        if value_add != value:
            if value not in self.d and not common.is_simple_number(value) and not common.is_simple_bool(value) and common.is_variable(value):
                if common.is_relational(value, value_add):
                    self.d[value] = value_add
                
    def __add_d_macro(self, value, macro):
        if value not in self.d_macro and not common.is_simple_number(value) and not common.is_simple_bool(value) and common.is_variable(value):
            self.d_macro[value] = macro

    def get_variable_change(self):
        return self.d

    def get_variable_add_macro(self):
        return self.d_macro
    
    def get_all_file_path(self):
        return self.path

