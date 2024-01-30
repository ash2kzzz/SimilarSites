#!/usr/bin/env python3

import constants
from enum import IntEnum

class statement_ctx_type(IntEnum):
    unknown = 0
    func_statement = 1
    goto_statement = 2

class lock_ctx_type(IntEnum):
    unknown = 0
    spin_lock = 1
    read_lock = 2
    write_lock = 3
    mutex_lock = 4
    sem_lock = 5
    prepare_lock = 6
    enable_lock = 7
    rcu_lock = 8
    rcu_read_lock = 9

class StatementCTXInfo(object):
    def __init__(self, ctx_line):
        have_func_ctx = constants.FUNC_NAME.match(ctx_line.strip())
        if have_func_ctx:
            self.ctx_type = statement_ctx_type.func_statement
            self.ctx = have_func_ctx.group(1) + '\('
            return
        have_goto_ctx = constants.GOTO_LABLE.match(ctx_line.strip())
        if have_goto_ctx:
            self.ctx_type = statement_ctx_type.goto_statement
            self.ctx = 'goto ' + have_goto_ctx.group(1) + ';'
            return
        self.ctx_type = statement_ctx_type.unknown
        self.ctx = ''

class LockCTXInfo(object):
    def __init__(self, func_name_list, ctx_type, ctx_args_list):
        self.ctx_type = ctx_type
        self.ctx_args_list = ctx_args_list # list
        self.func_name_list = func_name_list # list[tuple] tuple(func_name, func_args:list)

