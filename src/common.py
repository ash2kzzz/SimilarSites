#!/usr/bin/env python3

import re
import constants
import ctx
import lockers

SEARCH_LINES = 7
CHECK_LINES = 5

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

def get_judge_conditions(remove_condition_list, add_condition_list):
    judge_conditions = []
    for condition in remove_condition_list:
        if condition in add_condition_list and not is_simple_number(condition) and not is_simple_bool(condition):
            judge_conditions.append(condition)
    return judge_conditions

def get_change_conditions(remove_condition_list, add_condition_list):
    change_conditions = []
    for condition in add_condition_list:
        if condition not in remove_condition_list and not is_simple_number(condition) and not is_simple_bool(condition):
            change_conditions.append(condition)
    return change_conditions

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
    return m.group(1)

def is_lock_statement(line):
    m = constants.LOCK_NAME.match(line.strip())
    if not m:
        return False
    line = m.group(1)
    for lock_list in lockers.all_lock_list:
        if line in lock_list:
            return True
    return False

def is_unlock_statement(line):
    m = constants.LOCK_NAME.match(line.strip())
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
    line = constants.LOCK_NAME.match(line.strip()).group(1)
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
    line = constants.LOCK_NAME.match(line.strip()).group(1)
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

def search_forward_lock(line_list, index, lock_type):
    # index for the first
    if index == 0:
        return 0
    search_lines = SEARCH_LINES
    line_no = index
    while search_lines > 0:
        if is_lock_statement(line_list[line_no]) and statement_lock_type(line_list[line_no]) == lock_type:
            return line_no
        search_lines -= 1
        line_no -= 1
        if line_no < 0:
            return 0
    return 0

def search_backward_unlock(line_list, index, lock_type):
    # index for the first
    if index == 0:
        return 0
    search_lines = SEARCH_LINES
    line_no = index
    while search_lines > 0:
        if is_unlock_statement(line_list[line_no]) and statement_unlock_type(line_list[line_no]) == lock_type:
            return line_no
        search_lines -= 1
        line_no += 1
        if line_no >= len(line_list):
            return 0
    return 0

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

