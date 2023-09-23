#!/usr/bin/env python3

import re

pattern = re.compile(r'Fixes:[ ]?(commit )?([0-9a-fA-F]{12,})')

COMMIT_ID = re.compile(r'From ([\w]{40})')
PATH_COMMIT_ID = re.compile(r'(/\w+)+/([\w]{40}).patch')

FUNC_NAME = re.compile(r'(\w+)\(')
GOTO_LABLE = re.compile(r'goto (\w+);')
LOCK_NAME = re.compile(r'(\w+)\(')
DEFINE_STATEMENT = re.compile(r'(\w+ )+(\w+)\(')

EXPR = re.compile(r'(\w+(\->\w+)*)\s+=\s+((\w+)\((\w+(\->\w+)*)\)|(\w+(\->\w+)*));')
COMPARE = re.compile(r'((\w+)\((\w+(\->\w+)*)\)|(\w+(\->\w+)*))\s+(==|!=|>|<|<=|<=)\s+((\w+)\((\w+(\->\w+)*)\)|(\w+(\->\w+)*))')
FUNC_CALL = re.compile(r'(\w+)\((\w+(\->\w+)*), (\w+(\->\w+)*)\)')

VARIABLE = re.compile(r'((\w+)\((\w+(\->\w+)*)\)|(\w+(\->\w+)*))')

IDENTIFIER = re.compile(r'(\w+)')
DEREF = re.compile(r'((\w+)\->\w+)')
MACRO = re.compile(r'(\w+)\((\w+|\w+\->\w+)\)')