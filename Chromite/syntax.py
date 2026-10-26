"""

Chromite/syntax.py
~~~~~~~~~~~~~~~~~~
Functionality for outputting text with syntax highlighting and displaying text in an editor format.

Copyright (C) 2026 NastyaNoTamashii.
License: MIT
Author: NastyaNoTamashii

"""

__all__ = ['Syntax', 'make_editor']

import re
from dataclasses import dataclass, replace
from typing import Dict, Any, Optional
from .fmt import Color, ColorBG
from ._types import StyleType
from ._syntax_map import SYNTAX_MAP
import shutil

# Editor themes
@dataclass(frozen=True)
class _CodeColorSheme:
    # --- VS Code Dark+ code color sheme  --- 
    kwc: StyleType = Color.rgb(197, 134, 192)  # Keyword control: Purple (if, elif, return)
    kws: StyleType = Color.rgb(86, 156, 214)   # Keyword storage: Blue (def, class, const)
    fc:  StyleType = Color.rgb(220, 220, 170)  # Functions call: Yellow (myfunc())
    fd:  StyleType = Color.rgb(220, 220, 170)  # Func def: Yellow (def)
    cd:  StyleType = Color.rgb(78, 201, 176)   # Class def: Turquoise (class)
    b:   StyleType = Color.rgb(78, 201, 176)   # Builtin: Turquoise - Basic built-in functions (print, len)
    c:   StyleType = Color.rgb(86, 156, 214)   # Constant: Blue (const)
    var: StyleType = Color.rgb(156, 220, 254)  # Variable: Light blue (var)
    s:   StyleType = Color.rgb(206, 145, 120)  # String: Orange ("", '')
    n:   StyleType = Color.rgb(181, 206, 168)  # Interable: Light green (123)
    com: StyleType = Color.rgb(106, 153, 85)   # Comment: Green (#, //)

    def copy(self, **changes) -> "EditorTheme":
        """Copy the style with changes"""
        return replace(self, **changes)

class CodeColorSheme:
    """Code color theme: Visual Studio Dark+."""
    VS_code_DarkPlus = _CodeColorSheme()

class Syntax:
    @classmethod
    def _core_highlight(
        cls,
        code: str,
        lang: str, 
        func_defs: set,
        class_defs: set, 
        func_calls: set, 
        var_decls: set,
        theme: _CodeColorSheme = CodeColorSheme.VS_code_DarkPlus
    ) -> str:
        lang_config: Dict[str, Any] = SYNTAX_MAP.get(lang, {})
        
        ctrl_kw = lang_config.get('control_keywords', set())
        stor_kw = lang_config.get('storage_keywords', set())
        constants = lang_config.get('constants', set())
        builtins = lang_config.get('builtins', set())
        
        comments_patterns = lang_config.get('comments', [r'//.*'])
        strings_patterns = lang_config.get('strings', [r'\".*?\"', r'\'.*?\''])
        
        comment_regexes = []
        for p in comments_patterns:
            if '/*' in p or '"""' in p or "'''" in p:
                comment_regexes.append(re.compile(f'^({p})', re.DOTALL))
            else:
                safe_p = p.replace('.*', '[^\\n]*')
                comment_regexes.append(re.compile(f'^({safe_p})'))

        string_regexes = [re.compile(f'^({p})', re.DOTALL) for p in strings_patterns]
        
        number_regex = re.compile(r'^(\b\d+(?:\.\d+)?\b)')
        ident_regex = re.compile(r'^(\$[a-zA-Z_][a-zA-Z0-9_]*|\@[a-zA-Z_][a-zA-Z0-9_]*|\b[a-zA-Z_][a-zA-Z0-9_]*\b)')
        ws_regex = re.compile(r'^(\s+)')

        result = []
        i = 0
        length = len(code)

        while i < length:
            chunk = code[i:]
            matched = False

            for rx in comment_regexes:
                m = rx.match(chunk)
                if m:
                    val = m.group(1)
                    result.append(f"{theme.com}{val}{Color.RESET}")
                    i += len(val)
                    matched = True
                    break
            if matched:
                continue

            for rx in string_regexes:
                m = rx.match(chunk)
                if m:
                    val = m.group(1)
                    result.append(f"{theme.s}{val}{Color.RESET}")
                    i += len(val)
                    matched = True
                    break
            if matched:
                continue

            m = number_regex.match(chunk)
            if m:
                val = m.group(1)
                result.append(f"{theme.n}{val}{Color.RESET}")
                i += len(val)
                continue

            m = ident_regex.match(chunk)
            if m:
                name_val = m.group(1)
                if name_val in stor_kw:
                    result.append(f"{theme.kws}{name_val}{Color.RESET}")
                elif name_val in ctrl_kw:
                    result.append(f"{theme.kwc}{name_val}{Color.RESET}")
                elif name_val in constants:
                    result.append(f"{theme.c}{name_val}{Color.RESET}")
                elif name_val in class_defs:
                    result.append(f"{theme.cd}{name_val}{Color.RESET}")
                elif name_val in func_defs:
                    result.append(f"{theme.fd}{name_val}{Color.RESET}")
                elif name_val in func_calls:
                    result.append(f"{theme.fc}{name_val}{Color.RESET}")
                elif name_val in builtins or name_val.startswith('@'):
                    result.append(f"{theme.b}{name_val}{Color.RESET}")
                elif name_val in var_decls or name_val.startswith('$'):
                    result.append(f"{theme.var}{name_val}{Color.RESET}")
                else:
                    result.append(name_val)
                i += len(name_val)
                continue

            m = ws_regex.match(chunk)
            if m:
                val = m.group(1)
                result.append(val)
                i += len(val)
                continue

            result.append(code[i])
            i += 1

        return "".join(result)

    @classmethod
    def highlight(cls, code: str, lang: str = 'python') -> str:
        '''
        A universal method for highlighting any language.

        >>> mycode = """
        >>> #iostream
        >>> #include <vector>
        >>> #include <string>
        >>> 
        >>> class Engine {
        >>> public:
        >>>     void start() {
        >>>         std::cout << "Engine started!" << std::endl;
        >>>     }
        >>> };
        >>> 
        >>> int main() {
        >>>     Engine eng;
        >>>     eng.start();
        >>>     return 0;
        >>> }
        >>> """
        >>> print(highlight(mycode, lang = 'cpp'))
        '''
        lang = lang.lower()
        lang_config = SYNTAX_MAP.get(lang, SYNTAX_MAP['python'])
        
        extractor = lang_config.get('extractor')
        if extractor:
            func_defs, class_defs, var_decls = extractor(code)
        else:
            func_defs, class_defs, var_decls = set(), set(), set()

        func_calls = set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code)) - func_defs - class_defs

        return cls._core_highlight(code, lang, func_defs, class_defs, func_calls, var_decls)

    @classmethod
    def python(cls, code: str) -> str:
        return cls.highlight(code, 'python')

    @classmethod
    def js(cls, code: str) -> str:
        return cls.highlight(code, 'js')

    @classmethod
    def php(cls, code: str) -> str:
        return cls.highlight(code, 'php')

    @classmethod
    def zig(cls, code: str) -> str:
        return cls.highlight(code, 'zig')

    @classmethod
    def c(cls, code: str) -> str:
        return cls.highlight(code, 'c')

    @classmethod
    def cpp(cls, code: str) -> str:
        return cls.highlight(code, 'cpp')

    @classmethod
    def cs(cls, code: str) -> str:
        return cls.highlight(code, 'cs')

    @classmethod
    def rust(cls, code: str) -> str:
        return cls.highlight(code, 'rust')

    @classmethod
    def lua(cls, code: str) -> str:
        return cls.highlight(code, 'lua')

    @classmethod
    def java(cls, code: str) -> str:
        return cls.highlight(code, 'java')

    @classmethod
    def bash(cls, code: str) -> str:
        return cls.highlight(code, 'bash')

    @classmethod
    def shell(cls, code: str) -> str:
        return cls.highlight(code, 'shell')

    @classmethod
    def bat(cls, code: str) -> str:
        return cls.highlight(code, 'bat')

    @classmethod
    def css(cls, code: str) -> str:
        return cls.highlight(code, 'css')

    @classmethod
    def html(cls, code: str) -> str:
        return cls.highlight(code, 'html')

_ANSI_RE = re.compile(r'(\x1b\[[0-9;]*m)')

# Editor themes
@dataclass(frozen=True)
class _EditorTheme:
    # Visual Studio Code Dark+ theme
    bgc:  StyleType = ColorBG.rgb(30, 30, 30)  # Editor background
    bga:  StyleType = ColorBG.rgb(40, 42, 46)  # Active line background
    bgg:  StyleType = ColorBG.rgb(37, 37, 38)  # Gutter background
    bgt:  StyleType = ColorBG.rgb(50, 50, 52)  # Title backgound
    fgn:  StyleType = Color.rgb(110, 110, 110) # Numbers foreground
    fgna: StyleType = Color.rgb(220, 220, 220) # Active numbers foreground
    fgt:  StyleType = Color.rgb(180, 180, 180) # Title foreground

    def copy(self, **changes) -> "EditorTheme":
        """Copy the style with changes"""
        return replace(self, **changes)

class EditorTheme:
    """Editor theme: Visual Studio Dark+."""
    VS_code_DarkPlus = _EditorTheme()

def _cut(line: str, width: int) -> str:
    out, visible = [], 0
    for part in _ANSI_RE.split(line):
        if not part:
            continue
        if _ANSI_RE.fullmatch(part):
            out.append(part)
        else:
            chunk = part[:max(width - visible, 0)]
            out.append(chunk)
            visible += len(chunk)
            if visible >= width:
                break
    return ''.join(out) + Color.RESET

def _split_lines(text: str) -> list[str]:
    lines, active = [], ''
    for raw in text.split('\n'):
        lines.append(active + raw)
        for seq in _ANSI_RE.findall(raw):
            active = '' if seq == Color.RESET else seq
    return lines

def make_editor(code: str, lang: str = 'python', *, filename: Optional[str] = None, active_line: Optional[int] = None, width: Optional[int] = None, tab_size: int = 4, theme: _EditorTheme = EditorTheme.VS_code_DarkPlus) -> str:
    """Returns the highlighted code formatted as it appears in the editor. Returns a string."""
    cols = width or shutil.get_terminal_size((80, 24)).columns
    code = code.expandtabs(tab_size).rstrip('\n')
    lines = _split_lines(Syntax.highlight(code, lang))

    num_w = len(str(len(lines)))
    gutter_w = num_w + 4
    code_w = max(cols - gutter_w, 1)

    out = []

    if filename:
        title = f" {filename}  •  {lang} "
        out.append(f"{theme.bgt}{theme.fgt}{title.ljust(cols)}{Color.RESET}")

    for n, line in enumerate(lines, start=1):
        is_active = n == active_line
        bg = theme.bga if is_active else theme.bgc
        num_color = theme.fgna if is_active else theme.fgn

        gutter = f"{theme.bgg}{num_color} {n:>{num_w}} {theme.fgn}│ {Color.RESET}"
        body = _cut(line, code_w).replace(Color.RESET, Color.RESET + bg)
        pad = ' ' * (code_w - len(_ANSI_RE.sub('', body)))
        out.append(f"{gutter}{bg}{body}{pad}{Color.RESET}")

    return '\n'.join(out)