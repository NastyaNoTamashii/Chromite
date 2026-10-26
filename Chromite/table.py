"""

Chromite/table.py
~~~~~~~~~~~~~~~~~
Creating powerful and practical tables.

Copyright (C) 2026 NastyaNoTamashii.
License: MIT
Author: NastyaNoTamashii

"""

__all__ = ['Table', 'TableStyle']

import re
import unicodedata
from dataclasses import dataclass, replace
from .codes import validate_compose, apply_compose, compose_to_ansi
from .fmt import BaseCodes
from ._base import Renderable
from ._markup import parse_markup
from ._types import StyleType

# Any style reset: After that, the table color must be reapplied
_RESET = re.compile(r"\x1b\[0?m|" + re.escape(str(BaseCodes.RESET)))

# Table styles
@dataclass(frozen=True)
class _Style:
    h: str = "─"                # Horizontal line
    v: str = "│"                # Vertical line
    tl: str = "┌"               # Corner top-left
    tr: str = "┐"               # Corner top-right
    bl: str = "└"               # Corner bottom-left
    br: str = "┘"               # Corner bottom-right
    down: str = "┬"             # Joint down
    up: str = "┴"               # Joint top
    right: str = "├"            # Joint right
    left: str = "┤"             # Joint left
    cross: str = "┼"            # Cross line
    top_h: str | None = None    # Top border line (None — same as h)
    head_h: str | None = None   # Line under the header
    bottom_h: str | None = None # Lower boundary line

    def copy(self, **changes) -> "TableStyle":
        """Copy the style with changes: ROUNDED.copy(h="=")"""
        return replace(self, **changes)

class TableStyle:
    """Different table styles: Single, Rounded, Double and ASCII."""
    Single = _Style()
    Rounded = _Style(tl="╭", tr="╮", bl="╰", br="╯")
    Double = _Style("═", "║", "╔", "╗", "╚", "╝", "╦", "╩", "╠", "╣", "╬")
    ASCII = _Style("-", "|", "+", "+", "+", "+", "+", "+", "+", "+", "+")

# Character width
# ANSI codes (SGR styles/colors and OSC references) take up 0 columns
_ANSI = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07\x1b]*(?:\x07|\x1b\\))")
_TOKEN = re.compile(_ANSI.pattern + "|.", re.S)  # ANSI code (entire code or a single character)
_ZWJ, _VS16 = "‍", "️"  # emoji joiner / emoji presentation selector

def _clusters(s):
    """Splits a string into [fragment, width] pieces. This is the single source of
    truth for width: _w measures with it and _put draws with it, so they never disagree.

    - ANSI codes: width 0.
    - Wide characters (CJK, most emoji): width 2.
    - Combining marks, invisible format characters (zero-width space, ZWJ, variation
      selectors) and skin tone modifiers are glued to the previous character.
    - Emoji sequences (ZWJ, VS16, skin tone) are one piece. VS16 widens a narrow
      character to 2 columns, as modern terminals do."""
    out, last, join = [], None, False  # last: last visible piece; join: previous char was ZWJ
    for tok in _TOKEN.findall(s):
        if len(tok) > 1:  # ANSI code
            out.append([tok, 0])
            continue
        glue = (join or unicodedata.category(tok) in ("Mn", "Me", "Cf")
                or "\U0001f3fb" <= tok <= "\U0001f3ff")
        if glue and last:
            last[0] += tok
            if tok == _VS16 and last[1] == 1:
                last[1] = 2
        elif glue:  # invisible character with nothing to attach to
            out.append([tok, 0])
        else:
            last = [tok, 2 if unicodedata.east_asian_width(tok) in "WF" else 1]
            out.append(last)
        join = tok == _ZWJ and last is not None
    return out

def _w(s):
    """Number of terminal columns the string occupies when printed."""
    return sum(w for _, w in _clusters(s))


def _prepare(text, compose) -> str:
    """The single entry point for any text going into the table:
    $style$ / :emoji: markup -> ANSI codes / emoji (so width is measured on what is
    really printed), then 'compose' is applied."""
    text = parse_markup(str(text))
    codes = _ANSI.findall(text)
    if codes and not _RESET.fullmatch(codes[-1]):  # a style opened by markup must not leak out of the cell
        text += str(BaseCodes.RESET)
    return apply_compose(text, compose)

def _align(text, width, align):
    gap = width - _w(text)
    if align == "right":
        return " " * gap + text
    if align == "center":
        return " " * (gap // 2) + text + " " * (gap - gap // 2)
    return text + " " * gap

def _put(row, pos, s):
    """Writes a string into a row of cells (wide characters take up two cells).
    Zero-width pieces (ANSI codes, invisible characters) are appended to the previous cell."""
    for frag, cw in _clusters(s):
        if cw == 0:
            row[pos - 1] += frag
            continue
        row[pos] = frag
        for k in range(1, cw):
            row[pos + k] = ""
        pos += cw

# Stores data for a single column.
class _Col:
    def __init__(self, title, key, align):
        self.title, self.key, self.align, self.children = title, key, align, []

class Table(Renderable):
    __slots__ = ("style", "compose", "padding", "row_lines", "_cols", "_roots", "_rows",)

    def __init__(
        self,
        style: TableStyle = TableStyle.Single,
        compose: StyleType = None,
        padding = 1,
        row_lines = False
    ):
        """
        :param style: Table Design Style (Single, Rounded, Double, ASCII).
        :param compose: ANSI style or sequence of styles (Color, ColorBG, Style) applied to the entire text string.
        :param padding: Spaces on the left and right sides of a cell.
        :param row_lines: Space between lines.
        """
        self.style = style
        self.compose = compose
        self.padding = padding
        self.row_lines = row_lines
        self._cols = {} # key -> _Col
        self._roots = []
        self._rows = []

        validate_compose(self.compose)

    def add_column(self, title, compose: StyleType = None, key=None, parent=None, align="left"):
        """
        Adds a column to the table and returns its key.

        Columns can be nested: a column with children becomes a group header
        spanning all of them, and the data cells belong to the lowest-level columns.

        >>> table.add_column("Name")
        >>> table.add_column("City", align="right")
        >>> table.add_column("Contacts")                       # group header
        >>> table.add_column("Email", parent="Contacts")
        >>> table.add_column("Phone", parent="Contacts", key="phone")

        :param title: Header text. Supports Chromite markup (e.g. "$bold$Name").
        :param compose: ANSI style or sequence of styles (Color, ColorBG, Style) applied to the header text.
        :param key: Unique column identifier used to address it in rows given as dicts and in 'parent'. Defaults to 'title'.
        :param parent: Key of an existing column to nest this one under, as a sub-column of a group header. If None, the column is top-level.
        :param align: Alignment of the cell contents: "left", "right" or "center". Header text is always centered.
        :return: The column key (the same as 'key', or 'title' if 'key' was not given).
        :raises ValueError: If a column with this key already exists.
        :raises KeyError: If 'parent' does not match any existing column.
        """
        validate_compose(compose)

        key = title if key is None else key
        if key in self._cols:
            raise ValueError(f"The '{key}' column already exists—please specify a different key")
        if parent is not None and parent not in self._cols:
            raise KeyError(f"The parent column '{parent}' was not found")
        col = _Col(_prepare(title, compose), key, align)
        (self._roots if parent is None else self._cols[parent].children).append(col)
        self._cols[key] = col
        return key

    def add_row(self, *values, compose: StyleType = None):
        """
        Adds a row to the table and returns the table itself, so calls can be chained.

        A row can be given in two ways:
        - positionally, one value per column in left-to-right order
        (for nested columns, the lowest-level columns are counted);
        - as a single dict, where keys are column keys.

        >>> table.add_row("Nastiya", "Odesa", 18)
        >>> table.add_row({"Name": "Nastiya", "Age": 18})   # By column key.
        >>> table.add_row("Nastiya").add_row("Olya")        # Chaining.

        Missing values are shown as empty cells: fewer positional values than
        columns, a key absent from the dict, or None. Line breaks inside a value
        are replaced with spaces. Values support Chromite markup.

        :param values: The cell values (any type, converted to str), or a single dict {column key: value}.
        :param compose: ANSI style or sequence of styles (Color, ColorBG, Style) applied to every value in this row.
        :return: The table itself.

        Note: more positional values than columns raises ValueError when the table
        is rendered, not when the row is added. Dict keys that match no column are
        ignored.
        """
        validate_compose(compose)

        def style(v):
            return v if v is None else _prepare(v, compose)

        one = values[0] if len(values) == 1 else None
        if isinstance(one, dict):
            self._rows.append({k: style(v) for k, v in one.items()})
        else:
            self._rows.append(tuple(style(v) for v in values))
        return self

    def add_rows(self, rows, compose: StyleType = None):
        """
        Adds several rows at once. Each row is handled like in add_row(): a
        list/tuple of values (one per column) or a dict {column key: value}.
        Both kinds can be mixed in one call.

        >>> table.add_rows([("Olya", "Kyiv", 19), ["Nastiya", "Odesa", 18]])
        >>> table.add_rows([
        ...     {"Name": "Veronika", "City": "Kyiv"},
        ...     {"Name": "Nastiya", "City": "Odesa"},
        ... ])

        :param rows: An iterable of rows (lists, tuples or dicts).
        :param compose: ANSI style or sequence of styles (Color, ColorBG, Style) applied to every value in every added row.
        """
        for r in rows:
            if isinstance(r, dict):
                self.add_row(r, compose=compose)
            else:
                self.add_row(*r, compose=compose)
        return self

    def _layout(self):
        """Leaves and nodes (col, level, start, end) in leaf coordinates."""
        leaves, nodes = [], []

        def walk(cols, level):
            for c in cols:
                start = len(leaves)
                if c.children:
                    walk(c.children, level + 1)
                else:
                    leaves.append(c)
                nodes.append((c, level, start, len(leaves)))

        walk(self._roots, 0)
        return leaves, nodes

    def flush(self) -> str:
        leaves, nodes = self._layout()
        if not leaves:
            raise ValueError("There are no columns in the table.")
        st, pad, n = self.style, self.padding, len(leaves)
        depth = max(lv for _, lv, _, _ in nodes) + 1

        def cell(v):
            return "" if v is None else str(v).replace("\n", " ")

        data = []
        for r in self._rows:
            if isinstance(r, dict):
                data.append([cell(r.get(c.key)) for c in leaves])
            elif len(r) > n:
                raise ValueError(f"In the line {len(r)} values, and {n} leaf columns")
            else:
                data.append([cell(v) for v in r] + [""] * (n - len(r)))

        # Leaf width, then adjust the spacing under the group headings.
        w = [max([_w(c.title)] + [_w(r[i]) for r in data]) + 2 * pad
             for i, c in enumerate(leaves)]
        for c, _, s, e in nodes:
            if c.children:
                extra = _w(c.title) + 2 * pad - (sum(w[s:e]) + e - s - 1)
                for k in range(max(extra, 0)):
                    w[s + k % (e - s)] += 1
        x = [0]
        for wi in w:
            x.append(x[-1] + wi + 1)

        # Rows and columns: H — horizontal segments (row, column); V — vertical segments (row, border).
        H, V, texts = set(), set(), {}
        for c, lv, s, e in nodes:
            b = lv if c.children else depth - 1 # The leaves extend all the way to the bottom of the header.
            H.update((y, i) for i in range(s, e) for y in (2 * lv, 2 * b + 2))
            V.update((y, j) for y in range(2 * lv + 1, 2 * b + 2, 2) for j in (s, e))
            texts.setdefault(lv + b + 1, []).append((x[s] + 1, x[e] - x[s] - 1, c.title, "center"))
        head = 2 * depth
        for k, r in enumerate(data):
            y = head + 1 + 2 * k
            V.update((y, j) for j in range(n + 1))
            if self.row_lines or k == len(data) - 1:
                H.update((y + 1, i) for i in range(n))
            texts.setdefault(y, []).extend(
                (x[i] + 1, w[i], r[i], c.align) for i, c in enumerate(leaves))
        total = head + 1 + 2 * len(data)

        def hchar(y):
            if y == 0:
                return st.top_h or st.h
            if y == total - 1:
                return st.bottom_h or st.h
            if y == head:
                return st.head_h or st.h
            return st.h

        base = compose_to_ansi(self.compose)
        lines = []
        for y in range(total):
            row = [" "] * (x[-1] + 1)
            if y % 2 == 0:  # Separator line.
                if not any((y, i) in H for i in range(n)):
                    continue
                for i in range(n):
                    if (y, i) in H:
                        row[x[i] + 1:x[i] + w[i] + 1] = [hchar(y)] * w[i]
                for j in range(n + 1):
                    key = ((y - 1, j) in V, (y + 1, j) in V,
                           j > 0 and (y, j - 1) in H, j < n and (y, j) in H)
                    row[x[j]] = {
                        (0, 1, 0, 1): st.tl, (0, 1, 1, 0): st.tr,
                        (1, 0, 0, 1): st.bl, (1, 0, 1, 0): st.br,
                        (0, 1, 1, 1): st.down, (1, 0, 1, 1): st.up,
                        (1, 1, 0, 1): st.right, (1, 1, 1, 0): st.left,
                        (1, 1, 1, 1): st.cross, (1, 1, 0, 0): st.v,
                        (0, 0, 1, 1): hchar(y),
                    }.get(tuple(map(int, key)), " ")
            else:
                for j in range(n + 1):
                    if (y, j) in V:
                        row[x[j]] = st.v
            for x0, width, t, al in texts.get(y, []):
                inner = _align(t, width - 2 * pad, al)
                _put(row, x0, " " * pad + inner + " " * pad)
            line = "".join(row)
            if base:  # After resetting the cell style, the table color reappears.
                line = base + _RESET.sub(lambda m: m.group() + base, line) + str(BaseCodes.RESET)
            lines.append(line)
        return "\n".join(lines)