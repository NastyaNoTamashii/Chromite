"""

Chromite/syntax.py
~~~~~~~~~~~~~~~~~~
Functionality for outputting text with syntax highlighting and displaying text in an editor format.

Copyright (C) 2026 NastyaNoTamashii.
License: MIT
Author: NastyaNoTamashii

"""

__all__ = ['Syntax', 'Editor', 'SyntaxTheme', 'EditorTheme']

import re
from dataclasses import dataclass, replace
from typing import Dict, Any, Optional
from .terminal import place
from .fmt import Color, ColorBG
from ._base import Renderable
from ._types import StyleType, PosType
from ._text import _cut
from ._syntax_map import SYNTAX_MAP
import shutil

# Editor themes
@dataclass(frozen=True)
class _SyntaxTheme:
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

    def copy(self, **changes) -> "SyntaxTheme":
        """Copy the style with changes"""
        return replace(self, **changes)

class SyntaxTheme:
    """Code color theme: Visual Studio Dark+."""
    VS_code_DarkPlus = _SyntaxTheme()

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

class Syntax(Renderable):
    __slots__ = ("code", "lang", "theme", "pos", "lang_config",)

    def __init__(
        self,
        code: str,
        lang: str = "python",
        *,
        theme: SyntaxTheme = SyntaxTheme.VS_code_DarkPlus,
        pos: PosType = None
    ):
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
        self.code = code
        self.lang = lang
        self.theme = theme
        self.pos = pos

        self.lang_config = SYNTAX_MAP.get(lang.lower(), None)

        if self.lang_config == None:
            raise ValueError(f'No language with the name "{lang}" was found. Check _syntax_map.py to see which languages are supported.')

    @classmethod
    def _core_highlight(
        cls,
        code: str,
        lang: str, 
        func_defs: set,
        class_defs: set, 
        func_calls: set, 
        var_decls: set,
        theme: _SyntaxTheme = SyntaxTheme.VS_code_DarkPlus
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

    def flush(self) -> str:
        extractor = self.lang_config.get('extractor')
        if extractor:
            func_defs, class_defs, var_decls = extractor(self.code)
        else:
            func_defs, class_defs, var_decls = set(), set(), set()

        func_calls = set(re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', self.code)) - func_defs - class_defs

        return place(self._core_highlight(self.code, self.lang.lower(), func_defs, class_defs, func_calls, var_decls), self.pos)

    @classmethod
    def python(cls, code, **kw):
        return cls(code, "python", **kw)

    @classmethod
    def js(cls, code, **kw):
        return cls(code, "js", **kw)

    @classmethod
    def php(cls, code, **kw):
        return cls(code, "php", **kw)

    @classmethod
    def zig(cls, code, **kw):
        return cls(code, "zig", **kw)

    @classmethod
    def c(cls, code, **kw):
        return cls(code, "c", **kw)

    @classmethod
    def cpp(cls, code, **kw):
        return cls(code, "cpp", **kw)

    @classmethod
    def cs(cls, code, **kw):
        return cls(code, "cs", **kw)

    @classmethod
    def rust(cls, code, **kw):
        return cls(code, "rust", **kw)

    @classmethod
    def lua(cls, code, **kw):
        return cls(code, "lua", **kw)

    @classmethod
    def java(cls, code, **kw):
        return cls(code, "java", **kw)

    @classmethod
    def bash(cls, code, **kw):
        return cls(code, "bash", **kw)

    @classmethod
    def shell(cls, code, **kw):
        return cls(code, "shell", **kw)

    @classmethod
    def bat(cls, code, **kw):
        return cls(code, "bat", **kw)

    @classmethod
    def css(cls, code, **kw):
        return cls(code, "css", **kw)

    @classmethod
    def html(cls, code, **kw):
        return cls(code, "html", **kw)

_ANSI_RE = re.compile(r'(\x1b\[[0-9;]*m)')

def _split_lines(text: str) -> list[str]:
    lines, active = [], ''
    for raw in text.split('\n'):
        lines.append(active + raw)
        for seq in _ANSI_RE.findall(raw):
            active = '' if seq == Color.RESET else seq
    return lines

class Editor(Renderable):
    __slots__ = ("code", "lang", "filename", "active_line", "width", "tab_size", "theme", "syntax_theme", "pos",)

    def __init__(
        self,
        code: str,
        lang = "python",
        *,
        filename: str = None,
        active_line: int = None,
        width: int = None,
        tab_size = 4,
        theme: EditorTheme = EditorTheme.VS_code_DarkPlus,
        syntax_theme: SyntaxTheme = SyntaxTheme.VS_code_DarkPlus,
        pos: PosType = None
    ):
        self.code = code
        self.lang = lang
        self.filename = filename
        self.active_line = active_line
        self.width = width
        self.tab_size = tab_size
        self.theme = theme
        self.syntax_theme = syntax_theme
        self.pos = pos
    
    def flush(self) -> str:
        """Returns the highlighted code formatted as it appears in the editor. Returns a string."""
        cols = self.width or shutil.get_terminal_size((80, 24)).columns
        code = self.code.expandtabs(self.tab_size).rstrip('\n')
        lines = _split_lines(Syntax(code, self.lang).flush())

        num_w = len(str(len(lines)))
        gutter_w = num_w + 4
        code_w = max(cols - gutter_w, 1)

        out = []

        if self.filename:
            title = f" {self.filename}  •  {self.lang} "
            out.append(f"{self.theme.bgt}{self.theme.fgt}{title.ljust(cols)}{Color.RESET}")

        for n, line in enumerate(lines, start=1):
            is_active = n == self.active_line
            bg = self.theme.bga if is_active else self.theme.bgc
            num_color = self.theme.fgna if is_active else self.theme.fgn

            gutter = f"{self.theme.bgg}{num_color} {n:>{num_w}} {self.theme.fgn}│ {Color.RESET}"
            body = _cut(line, code_w).replace(Color.RESET, Color.RESET + bg)
            pad = ' ' * (code_w - len(_ANSI_RE.sub('', body)))
            out.append(f"{gutter}{bg}{body}{pad}{Color.RESET}")

        return '\n'.join(out)