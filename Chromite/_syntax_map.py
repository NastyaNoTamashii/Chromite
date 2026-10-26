"""

Chromite/_syntax_map.py
~~~~~~~~~~~~~~~~~~~~~~~
Programming languages syntax map.

Supports:
- Python
- JS
- php
- zig
- c
- CS
- CPP
- Rust
- Lua
- Java
- Bash
- Shell
- Bat
- CSS
- HTML

Copyright (C) 2026 NastyaNoTamashii.
License: MIT
Author: NastyaNoTamashii

"""

import re
from typing import Dict, Any

SYNTAX_MAP: Dict[str, Dict[str, Any]] = {
    'python': {
        'control_keywords': {
            'return', 'if', 'elif', 'else', 'for', 'while', 
            'import', 'from', 'as', 'in', 'is', 'not', 'and', 'or', 
            'try', 'except', 'raise', 'with', 'yield', 'break', 'continue'
        },
        'storage_keywords': {'def', 'class', 'lambda', 'async', 'await'},
        'constants': {'True', 'False', 'None'},
        'builtins': {
            'print', 'len', 'range', 'str', 'int', 'dict', 'set', 
            'list', 'open', 'type', 'isinstance', 'super', 'enumerate'
        },
        'comments': [r'#.*'],
        'strings': [r'f?\"\"\"[\s\S]*?\"\"\"', r'f?\'\'\'[\s\S]*?\'\'\'', r'f?\".*?\"', r'f?\'.*?\''],
        'var_prefix': '',
        'extractor': lambda code: (
            set(re.findall(r'\bdef\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', code)),
            set(re.findall(r'\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', code)),
            set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*[:=]', code))
        )
    },
    'js': {
        'control_keywords': {
            'return', 'if', 'else', 'for', 'while', 'export', 'import', 
            'from', 'switch', 'case', 'break', 'continue', 'try', 'catch', 'throw'
        },
        'storage_keywords': {'const', 'let', 'var', 'function', 'class', 'new', 'async', 'await', 'typeof', 'instanceof'},
        'constants': {'true', 'false', 'null', 'undefined', 'NaN'},
        'builtins': {
            'console', 'window', 'document', 'process', 'Object', 
            'Array', 'String', 'Math', 'Number', 'Promise', 'JSON'
        },
        'comments': [r'/\*[\s\S]*?\*/', r'//.*'],
        'strings': [r'`[\s\S]*?`', r'\".*?\"', r'\'.*?\''],
        'var_prefix': '',
        'extractor': lambda code: (
            set(re.findall(r'\bfunction\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', code)),
            set(re.findall(r'\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', code)),
            set(re.findall(r'\b(?:const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', code))
        )
    },
    'php': {
        'control_keywords': {
            'return', 'if', 'else', 'elseif', 'for', 'foreach', 'while', 
            'use', 'namespace', 'switch', 'case', 'break', 'continue', 'try', 'catch'
        },
        'storage_keywords': {
            'function', 'class', 'public', 'private', 'protected', 
            'static', 'final', 'new', 'interface', 'trait'
        },
        'constants': {'true', 'false', 'null', 'TRUE', 'FALSE', 'NULL'},
        'builtins': {'echo', 'print_r', 'var_dump', 'include', 'require', 'die', 'exit', 'array'},
        'comments': [r'/\*[\s\S]*?\*/', r'//.*', r'#.*'],
        'strings': [r'\".*?\"', r'\'.*?\''],
        'var_prefix': '$',
        'extractor': lambda code: (
            set(re.findall(r'\bfunction\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', code)),
            set(re.findall(r'\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', code)),
            set(re.findall(r'(\$[a-zA-Z_][a-zA-Z0-9_]*)\b', code))
        )
    },
    'zig': {
        'control_keywords': {
            'if', 'else', 'switch', 'while', 'for', 'return', 
            'break', 'continue', 'try', 'catch', 'defer', 'errdefer', 'pub'
        },
        'storage_keywords': {
            'fn', 'const', 'var', 'struct', 'enum', 'union', 
            'opaque', 'usingnamespace', 'linksection', 'align', 'allowzero'
        },
        'constants': {'true', 'false', 'null', 'undefined'},
        'builtins': {
            '@import', '@as', '@intCast', '@floatCast', '@panic', 
            '@print', '@sqrt', '@TypeOf', '@sizeOf', '@alignOf',
            'i8', 'i16', 'i32', 'i64', 'i128', 'isize',
            'u8', 'u16', 'u32', 'u64', 'u128', 'usize',
            'f16', 'f32', 'f64', 'f80', 'f128', 'bool', 'void', 'type'
        },
        'comments': [r'//[/!].*', r'//.*'],
        'strings': [r'\".*?\"', r'\'.*?\''],
        'var_prefix': '',
        'extractor': lambda code: (
            set(re.findall(r'\bfn\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', code)),
            set(re.findall(r'\b(?:const|var)\s+([A-Z][a-zA-Z0-9_]*)\s*=\s*(?:struct|enum|union)', code)),
            set(re.findall(r'\b(?:const|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', code))
        )
    },
    'c': {
        'control_keywords': {
            'if', 'else', 'switch', 'case', 'default', 'for', 'while', 
            'do', 'return', 'break', 'continue', 'goto', 'typedef', 'sizeof'
        },
        'storage_keywords': {
            'int', 'char', 'float', 'double', 'void', 'long', 'short', 
            'unsigned', 'signed', 'struct', 'union', 'enum', 'extern', 
            'static', 'const', 'volatile', 'register', 'auto', 'inline'
        },
        'constants': {'NULL', 'true', 'false'},
        'builtins': {'printf', 'scanf', 'malloc', 'calloc', 'realloc', 'free', 'exit', 'stderr', 'stdout', 'stdin'},
        'comments': [r'/\*[\s\S]*?\*/', r'//.*'],
        'strings': [r'\".*?\"', r'\'.*?\''],
        'var_prefix': '',
        'extractor': lambda code: (
            set(re.findall(r'\b(?:int|char|float|double|void|long|short|unsigned|signed|[a-zA-Z_][a-zA-Z0-9_]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code)) - {'if', 'while', 'for', 'switch', 'return'},
            set(re.findall(r'\bstruct\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', code)),
            set(re.findall(r'\b(?:int|char|float|double|long|short|unsigned|signed|[a-zA-Z_][a-zA-Z0-9_]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:=|;|,)', code))
        )
    },
    'cpp': {
        'control_keywords': {
            'if', 'else', 'switch', 'case', 'default', 'for', 'while', 
            'do', 'return', 'break', 'continue', 'goto', 'try', 'catch', 'throw', 
            'new', 'delete', 'sizeof', 'decltype', 'template', 'typename', 'using', 'namespace'
        },
        'storage_keywords': {
            'int', 'char', 'float', 'double', 'void', 'bool', 'long', 'short', 
            'unsigned', 'signed', 'class', 'struct', 'enum', 'union', 'public', 
            'private', 'protected', 'virtual', 'override', 'final', 'const', 
            'constexpr', 'static', 'extern', 'inline', 'auto', 'friend', 'explicit'
        },
        'constants': {'nullptr', 'true', 'false', 'NULL'},
        'builtins': {
            'std', 'cout', 'cin', 'endl', 'vector', 'string', 'map', 'set', 
            'unique_ptr', 'shared_ptr', 'make_shared', 'make_unique', 'printf', 'scanf'
        },
        'comments': [r'/\*[\s\S]*?\*/', r'//.*'],
        'strings': [r'R\"\(.*?\)\"', r'\".*?\"', r'\'.*?\''],
        'var_prefix': '',
        'extractor': lambda code: (
            set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_<>:]*\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code)) - {'if', 'while', 'for', 'switch', 'catch', 'return'},
            set(re.findall(r'\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', code) + re.findall(r'\bstruct\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', code)),
            set(re.findall(r'\b(?:auto|int|char|float|double|bool|string|std::string)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:=|;|,)', code))
        )
    },
    'cs': {
        'control_keywords': {
            'if', 'else', 'switch', 'case', 'default', 'for', 'foreach', 'in', 
            'while', 'do', 'return', 'break', 'continue', 'goto', 'try', 'catch', 
            'finally', 'throw', 'async', 'await', 'yield', 'lock', 'using', 'namespace'
        },
        'storage_keywords': {
            'class', 'struct', 'interface', 'enum', 'record', 'public', 'private', 
            'protected', 'internal', 'static', 'readonly', 'virtual', 'override', 
            'abstract', 'sealed', 'partial', 'event', 'delegate', 'new', 'base', 'this', 'params'
        },
        'constants': {'true', 'false', 'null'},
        'builtins': {
            'int', 'string', 'bool', 'double', 'float', 'char', 'byte', 'long', 
            'short', 'decimal', 'object', 'var', 'void', 'Console', 'WriteLine', 'ReadLine',
            'Task', 'List', 'Dictionary', 'Array', 'Math', 'String', 'Exception'
        },
        'comments': [r'/\*[\s\S]*?\*/', r'//.*'],
        'strings': [r'@\"\".*?\"\"', r'\".*?\"', r'\'.*?\''],
        'var_prefix': '',
        'extractor': lambda code: (
            set(re.findall(r'\b(?:public|private|protected|internal|static|async|void|[A-Z][a-zA-Z0-9_<>]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code)) - {'if', 'while', 'for', 'switch', 'catch', 'return'},
            set(re.findall(r'\b(?:class|struct|interface|enum|record)\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', code)),
            set(re.findall(r'\b(?:var|[a-zA-Z_][a-zA-Z0-9_<>]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:=|;|,)', code))
        )
    },
    'rust': {
        'control_keywords': {
            'if', 'else', 'match', 'while', 'for', 'loop', 'return', 
            'break', 'continue', 'in', 'where', 'async', 'await', 'dyn'
        },
        'storage_keywords': {
            'fn', 'let', 'mut', 'const', 'static', 'struct', 'enum', 
            'trait', 'impl', 'pub', 'use', 'mod', 'crate', 'extern', 'ref', 'unsafe'
        },
        'constants': {'true', 'false', 'Some', 'None', 'Ok', 'Err'},
        'builtins': {
            'i8', 'i16', 'i32', 'i64', 'i128', 'isize',
            'u8', 'u16', 'u32', 'u64', 'u128', 'usize',
            'f32', 'f64', 'bool', 'char', 'str', 'String', 'Vec', 'Option', 'Result',
            'println!', 'print!', 'format!', 'vec!', 'panic!', 'assert!', 'todo!', 'dbg!'
        },
        'comments': [r'//[/!].*', r'//.*', r'/\*[\s\S]*?\*/'],
        'strings': [r'r#\".*?\"#', r'\".*?\"', r'\'.*?\''],
        'var_prefix': '',
        'extractor': lambda code: (
            set(re.findall(r'\bfn\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', code)),
            set(re.findall(r'\b(?:struct|enum|trait)\s+([A-Z][a-zA-Z0-9_]*)\b', code)),
            set(re.findall(r'\blet\s+(?:mut\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\b', code))
        )
    },
    'lua': {
        'control_keywords': {
            'if', 'then', 'elseif', 'else', 'end', 'for', 'while', 
            'do', 'repeat', 'until', 'return', 'break', 'in', 'goto'
        },
        'storage_keywords': {'function', 'local', 'and', 'or', 'not'},
        'constants': {'true', 'false', 'nil'},
        'builtins': {
            'print', 'type', 'tostring', 'tonumber', 'pairs', 'ipairs', 
            'select', 'error', 'assert', 'pcall', 'xpcall', 'setmetatable', 'getmetatable',
            'table', 'string', 'math', 'io', 'os', 'coroutine', 'debug'
        },
        'comments': [r'--\[\[[\s\S]*?\]\]', r'--.*'],
        'strings': [r'\[\[[\s\S]*?\]\]', r'\".*?\"', r'\'.*?\''],
        'var_prefix': '',
        'extractor': lambda code: (
            set(re.findall(r'\bfunction\s+([a-zA-Z_][a-zA-Z0-9_.]*)\b', code)),
            set(), # In Lua, classes/tables are usually declared using regular variables or metatables.
            set(r'\b(?:local\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*=' for _ in [0]) | set(re.findall(r'\blocal\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', code))
        )
    },
    'java': {
        'control_keywords': {
            'if', 'else', 'switch', 'case', 'default', 'for', 'while', 
            'do', 'return', 'break', 'continue', 'try', 'catch', 'finally', 
            'throw', 'throws', 'new', 'instanceof', 'assert', 'yield'
        },
        'storage_keywords': {
            'class', 'interface', 'enum', 'record', 'public', 'private', 
            'protected', 'static', 'final', 'abstract', 'synchronized', 
            'volatile', 'transient', 'native', 'strictfp', 'package', 'import', 'extens', 'implements'
        },
        'constants': {'true', 'false', 'null'},
        'builtins': {
            'String', 'Integer', 'Boolean', 'Double', 'Float', 'Long', 'Character',
            'System', 'out', 'println', 'print', 'Math', 'List', 'Map', 'Set', 
            'ArrayList', 'HashMap', 'HashSet', 'Object', 'Exception', 'Thread'
        },
        'comments': [r'/\*[\s\S]*?\*/', r'//.*'],
        'strings': [r'\".*?\"', r'\'.*?\''],
        'var_prefix': '',
        'extractor': lambda code: (
            set(re.findall(r'\b(?:public|private|protected|static|final|void|[A-Z][a-zA-Z0-9_<>]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code)) - {'if', 'while', 'for', 'switch', 'catch', 'return'},
            set(re.findall(r'\b(?:class|interface|enum|record)\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', code)),
            set(re.findall(r'\b(?:var|[a-zA-Z_][a-zA-Z0-9_<>]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:=|;|,)', code))
        )
    },
    'bash': {
        'control_keywords': {
            'if', 'then', 'else', 'elif', 'fi', 'for', 'in', 'do', 'done', 
            'while', 'until', 'case', 'esac', 'return', 'exit', 'source'
        },
        'storage_keywords': {'function', 'local', 'declare', 'readonly', 'export', 'set'},
        'constants': {'true', 'false'},
        'builtins': {
            'echo', 'printf', 'read', 'cd', 'pwd', 'eval', 'exec', 'trap', 
            'shift', 'test', 'true', 'false', 'history', 'alias', 'unalias'
        },
        'comments': [r'#.*'],
        'strings': [r'\".*?\"', r'\'.*?\''],
        'var_prefix': '$',
        'extractor': lambda code: (
            set(re.findall(r'\b(?:function\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*\)', code)),
            set(),
            set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)=', code))
        )
    },
    'shell': {
        'control_keywords': {
            'if', 'then', 'else', 'elif', 'fi', 'for', 'in', 'do', 'done', 
            'while', 'until', 'case', 'esac', 'return', 'exit'
        },
        'storage_keywords': {'local', 'export', 'readonly', 'set'},
        'constants': {'true', 'false'},
        'builtins': {'echo', 'printf', 'read', 'cd', 'pwd', 'eval', 'exec'},
        'comments': [r'#.*'],
        'strings': [r'\".*?\"', r'\'.*?\''],
        'var_prefix': '$',
        'extractor': lambda code: (
            set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*\)', code)),
            set(),
            set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)=', code))
        )
    },
    'bat': {
        'control_keywords': {
            'if', 'else', 'goto', 'for', 'in', 'do', 'call', 'exit', 'shift'
        },
        'storage_keywords': {'set', 'setlocal', 'endlocal'},
        'constants': {},
        'builtins': {
            'echo', 'pause', 'cls', 'rem', 'cd', 'dir', 'copy', 'move', 
            'del', 'start', 'taskkill', 'xcopy', 'robocopy'
        },
        'comments': [r'(?i)\bREM\b.*', r'::.*'],
        'strings': [r'\".*?\"'],
        'var_prefix': '%',
        'extractor': lambda code: (
            set(),
            set(),
            set(re.findall(r'\bset\s+([a-zA-Z_][a-zA-Z0-9_]*)=', code, re.IGNORECASE))
        )
    },
    'html': {
        'control_keywords': set(),
        'storage_keywords': {
            'html', 'head', 'body', 'div', 'span', 'p', 'a', 'ul', 'ol', 'li',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'tr', 'td', 'th',
            'form', 'input', 'button', 'section', 'article', 'nav', 'header',
            'footer', 'script', 'style', 'link', 'meta', 'title', 'img', 'br', 'hr'
        },
        'constants': {'true', 'false', 'utf-8', 'viewport'},
        'builtins': {'class', 'id', 'src', 'href', 'alt', 'type', 'name', 'value', 'placeholder'},
        'comments': [r'<!--[\s\S]*?-->'],
        'strings': [r'\".*?\"', r'\'.*?\''],
        'var_prefix': '',
        'extractor': lambda code: (
            set(),
            set(),
            set(re.findall(r'\b(class|id)\s*=\s*[\"\']([a-zA-Z_][a-zA-Z0-9_-]*)[\"\']', code))
        )
    },
    'css': {
        'control_keywords': {'media', 'import', 'keyframes', 'supports', 'charset'},
        'storage_keywords': {
            # More popular CSS
            'color', 'background', 'background-color', 'margin', 'padding',
            'width', 'height', 'display', 'position', 'font-size', 'font-family',
            'border', 'border-radius', 'flex', 'grid', 'align-items', 'justify-content',
            'top', 'left', 'right', 'bottom', 'opacity', 'transition', 'transform'
        },
        'constants': {'px', 'em', 'rem', 'vh', 'vw', '%', 'solid', 'flex', 'grid', 'block', 'inline', 'none', 'auto'},
        'builtins': {'rgb', 'rgba', 'hsl', 'var', 'calc'},
        'comments': [r'/\*[\s\S]*?\*/'],
        'strings': [r'\".*?\"', r'\'.*?\''],
        'var_prefix': '--',
        'extractor': lambda code: (
            set(),
            # .class, #id
            set(re.findall(r'([.#][a-zA-Z_][a-zA-Z0-9_-]*)', code)),
            # --var-name
            set(re.findall(r'(--[a-zA-Z_][a-zA-Z0-9_-]*)', code))
        )
    },
}