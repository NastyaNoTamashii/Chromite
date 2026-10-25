"""

Chromite/_syntax_map.py
~~~~~~~~~~~~~~~~~~~~~~~
Programming languages syntax map.

Supports:
- Python
- JS
- php

Copyright (C) 2026 NastyaNoTamashii.
License: MIT
Author: NastyaNoTamashii

"""

SYNTAX_MAP = {
    'python': {
        'keywords': {
            'def', 'class', 'return', 'if', 'elif', 'else', 'for', 'while', 
            'import', 'from', 'as', 'in', 'is', 'not', 'and', 'or', 'try', 'except'
        },
        'builtins': {'print', 'len', 'range', 'str', 'int', 'dict', 'set', 'list', 'open'}
    },
    'js': {
        'keywords': {
            'const', 'let', 'var', 'function', 'return', 'if', 'else', 'for', 'while', 
            'class', 'export', 'import', 'from', 'new', 'async', 'await', 'switch', 'case'
        },
        'builtins': {'console', 'log', 'window', 'document', 'process', 'Object', 'Array', 'String', 'Math'}
    },
    'php': {
        'keywords': {
            'function', 'return', 'if', 'else', 'for', 'foreach', 'while', 'class', 
            'public', 'private', 'protected', 'use', 'namespace', 'new', 'switch', 'case'
        },
        'builtins': {'echo', 'print_r', 'var_dump', 'include', 'require', 'die', 'exit', 'array'}
    }
}