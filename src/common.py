#!/usr/bin/env python3

import re
import constants
import ctx
import lockers

def complete_if_statement(line):
    stack = 1
    if line[:4] != "if (":
        return None
    for index, char in enumerate(line[4:]):
        if char == '(':
            stack += 1
        elif char == ')':
            stack -= 1
        if stack == 0:
            return line[:index+4+1]
    return None

def get_condition_list(if_str):

    def cond_strip(line):
        if line.startswith(r'(') and line.endswith(r')'):
            l = len(line)
            return cond_strip(line[1:l-1].strip())
        return line.strip()
    
    def cal_lp(line):
        count = 0
        for char in line:
            if char == '(':
                count += 1
        return count
    
    def cal_rp(line):
        count = 0
        for char in line:
            if char == ')':
                count += 1
        return count
    
    def cond_strip2(line):
        lp = cal_lp(line)
        rp = cal_rp(line)
        if lp == rp:
            return line
        if lp > rp:
            count = lp - rp
            return line[count:]
        if lp < rp:
            count = rp - lp
            return line[:-count]

    all_conditions = complete_if_statement(if_str)[3:]
    all_conditions = list(map(cond_strip, re.split('&&|\|\|', all_conditions)))
    return list(map(cond_strip2, all_conditions))

def the_same_conditions(condition_lis1, condition_lis2):
    if len(condition_lis1) != len(condition_lis2):
        return False
    for condition in condition_lis1:
        if condition not in condition_lis2:
            return False
    return True

def get_remove_base_conditions(remove_condition_list):
    remove_base_conditions = []
    for condition in remove_condition_list:
        if not is_simple_number(condition) and not is_simple_bool(condition):
            remove_base_conditions.append(condition)
    return remove_base_conditions

def get_base_conditions(remove_condition_list, add_condition_list):
    base_conditions = []
    for condition in remove_condition_list:
        if condition in add_condition_list and not is_simple_number(condition) and not is_simple_bool(condition):
            base_conditions.append(condition)
    return base_conditions

def get_extra_add_conditions(remove_condition_list, add_condition_list):
    extra_add_conditions = []
    for condition in add_condition_list:
        if condition not in remove_condition_list and not is_simple_number(condition) and not is_simple_bool(condition):
            extra_add_conditions.append(condition)
    return extra_add_conditions

def is_simple_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False

def is_simple_bool(s):
    if s == 'True' or s == 'true':
        return True
    if s == 'False' or s == 'false':
        return True
    return False

def is_variable(s):
    if constants.VARIABLE.match(s):
        return True
    return False
    
def capture_function_call(line):
    m = constants.FUNC_NAME.search(line.strip())
    if not m:
        return None
    d = constants.DEFINE_STATEMENT.match(line.strip())
    # remove some FP
    # list_for_each_entry_safe/list_del/list_add_tail
    if d or m.group(1).startswith(r'list_') or m.group(1).startswith(r'likely') or m.group(1).startswith(r'unlikely'):
        return None
    if "lock" in m.group(1) or "unlock" in m.group(1) or "bit" in m.group(1):
        return None
    return m.group(1)

def capture_function_args(line):
    m = constants.FUNC_ARGS.search(line.strip())
    if not m:
        return None
    d = constants.DEFINE_STATEMENT.match(line.strip())
    if d or m.group(1).startswith(r'list_') or m.group(1).startswith(r'likely') or m.group(1).startswith(r'unlikely'):
        return None
    if "lock" in m.group(1) or "unlock" in m.group(1) or "bit" in m.group(1):
        return None
    return m.group(2).split(", ")

def is_lock_statement(line):
    m = constants.FUNC_NAME.match(line.strip())
    if not m:
        return False
    line = m.group(1)
    for lock_list in lockers.all_lock_list:
        if line in lock_list:
            return True
    return False

def is_unlock_statement(line):
    m = constants.FUNC_NAME.match(line.strip())
    if not m:
        return False
    line = m.group(1)
    for unlock_list in lockers.all_unlock_list:
        if line in unlock_list:
            return True
    return False

def statement_lock_type(line):
    if not is_lock_statement(line):
        return ctx.lock_ctx_type.unknown
    line = constants.FUNC_NAME.match(line.strip()).group(1)
    if line in lockers.spin_lock_list:
        return ctx.lock_ctx_type.spin_lock
    if line in lockers.read_lock_list:
        return ctx.lock_ctx_type.read_lock
    if line in lockers.write_lock_list:
        return ctx.lock_ctx_type.write_lock
    if line in lockers.mutex_lock_list:
        return ctx.lock_ctx_type.mutex_lock
    if line in lockers.sem_lock_list:
        return ctx.lock_ctx_type.sem_lock
    if line in lockers.prepare_lock_list:
        return ctx.lock_ctx_type.prepare_lock
    if line in lockers.enable_lock_list:
        return ctx.lock_ctx_type.enable_lock
    if line in lockers.rcu_lock_list:
        return ctx.lock_ctx_type.rcu_lock
    if line in lockers.rcu_read_lock_list:
        return ctx.lock_ctx_type.rcu_read_lock
    return ctx.lock_ctx_type.unknown

def statement_unlock_type(line):
    if not is_unlock_statement(line):
        return ctx.lock_ctx_type.unknown
    line = constants.FUNC_NAME.match(line.strip()).group(1)
    if line in lockers.spin_unlock_list:
        return ctx.lock_ctx_type.spin_lock
    if line in lockers.read_unlock_list:
        return ctx.lock_ctx_type.read_lock
    if line in lockers.write_unlock_list:
        return ctx.lock_ctx_type.write_lock
    if line in lockers.mutex_unlock_list:
        return ctx.lock_ctx_type.mutex_lock
    if line in lockers.sem_unlock_list:
        return ctx.lock_ctx_type.sem_lock
    if line in lockers.prepare_unlock_list:
        return ctx.lock_ctx_type.prepare_lock
    if line in lockers.enable_unlock_list:
        return ctx.lock_ctx_type.enable_lock
    if line in lockers.rcu_unlock_list:
        return ctx.lock_ctx_type.rcu_lock
    if line in lockers.rcu_read_unlock_list:
        return ctx.lock_ctx_type.rcu_read_lock
    return ctx.lock_ctx_type.unknown

def lock_type_to_str(lock_type):
    if lock_type == ctx.lock_ctx_type.spin_lock:
        return "spin_lock"
    if lock_type == ctx.lock_ctx_type.read_lock:
        return "read_lock"
    if lock_type == ctx.lock_ctx_type.write_lock:
        return "write_lock"
    if lock_type == ctx.lock_ctx_type.mutex_lock:
        return "mutex_lock"
    if lock_type == ctx.lock_ctx_type.sem_lock:
        return "sem_lock"
    if lock_type == ctx.lock_ctx_type.prepare_lock:
        return "prepare_lock"
    if lock_type == ctx.lock_ctx_type.enable_lock:
        return "enable_lock"
    if lock_type == ctx.lock_ctx_type.rcu_lock:
        return "rcu_lock"
    if lock_type == ctx.lock_ctx_type.rcu_read_lock:
        return "rcu_read_lock"

def statement_lock_args(line):
    if not is_lock_statement(line) and not is_unlock_statement(line):
        return None
    return constants.FUNC_ARGS.match(line.strip()).group(2).strip("&")

def search_forward_lock(line_list, index, lock_type, lock_args):
    # index for the first
    if index == 0:
        return 0
    line_no = index
    while not start_of_function(line_list[line_no]) and line_no >= 0:
        if is_lock_statement(line_list[line_no]) and statement_lock_type(line_list[line_no]) == lock_type:
            if statement_lock_args(line_list[line_no]) == lock_args:
                return line_no
        line_no -= 1
        if line_no <= 0:
            return 0
    return 0

def search_backward_unlock(line_list, index, lock_type, lock_args):
    # index for the first
    if index == len(line_list):
        return 0
    line_no = index
    while not end_of_function(line_list[line_no]) and line_no <= len(line_list):
        if is_unlock_statement(line_list[line_no]) and statement_unlock_type(line_list[line_no]) == lock_type:
            if str_tail_match(statement_lock_args(line_list[line_no]), lock_args):
                return line_no
        line_no += 1
        if line_no >= len(line_list):
            return 0
    return 0

def function_in_line(line, tuple_list):
    func_name = capture_function_call(line)
    func_args = capture_function_args(line) # must have args
    if not func_name or not func_args:
        return False
    for func_n, func_a in tuple_list:
        if func_n != func_name:
            continue
        if list_tail_match(func_args, func_a) or list_tail_match(func_a, func_args):
            return True
    return False

def list_tail_match(list1, list2): # list2 greater than list1
    if len(list1) != len(list2):
        return False
    for a1 in list1:
        match_flag = 0
        for a2 in list2:
            if re.compile(add_escape(a1)+'$').search(a2):
                match_flag = 1
                break
        if match_flag == 0:
            return False
    return True

def str_tail_match(str1, str2):
    if re.compile(add_escape(str1)+'$').search(str2) or re.compile(add_escape(str2)+'$').search(str1):
        return True
    return False

def add_escape(str1):
    # * . ? + $ ^ [ ] ( ) { } | \ /
    escape_char = ["#", "*", ".", "?", "+", "$", "^", "[", "]", "(", ")", "{", "}", "|", "\\", "/"]
    str2 = ""
    for c in str1:
        if c in escape_char:
            str2 += "\\"+c
        else:
            str2 += c
    return str2

def is_assign_statement(line):
    if constants.EXPR.search(line.strip()):
        return True
    return False

def is_compare_statement(line):
    if constants.COMPARE.search(line.strip()):
        return True
    return False

def is_macro_statement(line):
    if constants.FUNC_CALL.search(line.strip()):
        return True
    return False

def assign_statement_get_value(line):
    if is_assign_statement(line):
        expr = constants.EXPR.search(line.strip())
        return (expr.group(1), expr.group(3))
    return None

def compare_statement_get_value(line):
    if is_compare_statement(line):
        compare = constants.COMPARE.search(line.strip())
        return (compare.group(1), compare.group(8))
    return None

def macro_statement_get_value(line):
    if is_macro_statement(line):
        macro = constants.FUNC_CALL.search(line.strip())
        return (macro.group(2), macro.group(4))
    return None

def macro_statement_get_macro(line):
    if is_macro_statement(line):
        macro = constants.FUNC_CALL.search(line.strip())
        return macro.group(1)
    return None

def is_debug_statement(line):
    if line.strip().startswith(r'pr_debug'):
        return True
    return False

def is_relational(old, new):
    if constants.IDENTIFIER.match(old):
        pattern = '(\w+)\(' + old + '\)'
        if re.compile(pattern).match(new):
            return True
    if constants.DEREF.match(old):
        m = constants.DEREF.match(old)
        all = m.group(1)
        body = m.group(2)
        pattern_all = '(\w+)\(' + str(all) + '\)'
        pattern_body = '(\w+)\(' + str(body) + '\)'
        if re.compile(pattern_all).match(new) or re.compile(pattern_body).match(new):
            return True
    if constants.MACRO.match(old):
        m = constants.MACRO.match(old)
        value = m.group(2)
        pattern = '(\w+)\(' + str(value) + '\)'
        if re.compile(pattern).match(new):
            return True
    return False

def reverse_condition_list(conditions_list):
    reverse_conditions = []
    for condition in conditions_list:
        if condition.startswith(r'!'):
            reverse_conditions.append(condition[1:])
        else:
            reverse_conditions.append('!'+condition)
    return reverse_conditions

def end_of_function(line):
    m = constants.END_OF_FUNCTION.match(line)
    if m:
        return True
    else:
        return False
    
def start_of_function(line):
    m = constants.START_OF_FUNCTION.match(line)
    if m:
        return True
    else:
        return False

