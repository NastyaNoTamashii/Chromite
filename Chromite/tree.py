"""

    Copyright (C) 2026 NastyaNoTamashii.

"""

__all__ = ['Tree', 'TreeStyle', 'Branch']

from typing import List as PyList, Union, Any, Tuple, Optional
from dataclasses import dataclass, replace
from .codes import ANSIElement, show_cursor, place, validate_compose, apply_compose
from .fmt import BaseCodes
from .io import Write

# Type Hint for styles: one element or list/tuple of elements
StyleType = Union[ANSIElement, PyList[ANSIElement], Tuple[ANSIElement, ...]]

PosType = Tuple[int, int]  # (x, y) or (col, row)

def _add_data(parent: Tree, data: dict | list | tuple) -> list[Branch]:
    """Convert a dict/list into nested branches within a parent element."""
    if isinstance(data, dict):
        items = [(str(k), v) for k, v in data.items()]
    else:
        items = [(i, v) for i, v in enumerate(data)]

    created: list[Branch] = []
    for key, value in items:
        if isinstance(value, (dict, list, tuple)) and value:
            branch = parent.add_branch(key)
            _add_data(branch, value)
        else:
            branch = parent.add_branch(value)
        created.append(branch)
    return created

# Table styles
@dataclass(frozen=True)
class _Style:
    branch: str = "├── "  # Horizontal line
    last: str =   "└── "  # Vertical line
    pipe: str =   "│   "  # Corner top-left
    space: str =  "    "  # Corner top-right
    
    def copy(self, **changes) -> "TreeStyle":
        """Copy the style with changes: ROUNDED.copy(h="=")"""
        return replace(self, **changes)

class TreeStyle:
    """Different tree styles: Single, Rounded, ASCII"""
    Single = _Style()
    Rounded = _Style(last="╰── ")

class Tree:
    __slots__ = ("label", "style", "compose", "branch_compose", "data", "pos", "max_depth", "children",)

    def __init__(
        self,
        label: Any = "root",
        *,
        style: TreeStyle = TreeStyle.Single,
        compose: StyleType = None,
        branch_compose: StyleType = None,
        data: Any = None,
        pos: Optional[PosType] = None,
        max_depth: int | None = None
    ) -> None:
        """
        Creates a tree of data.
        
        :param label: Main Tree label.
        :param compose: ANSI style or sequence of styles (Color, ColorBG, Style) applied to the tree item text.
        :param data: Accepts dict `{"My item": "Item"}` if specified
        :param pos: Optional (x, y) coordinates for precise terminal cursor positioning.
        :param max_depth: Maximum tree depth.
        """
        if isinstance(label, (dict, list, tuple)) and data is None:
            label, data = "root", label

        self.label = str(label)
        self.children: list[Branch] = []
        self.style = style
        self.compose = compose
        self.branch_compose = branch_compose
        self.pos = pos
        self.max_depth = max_depth

        validate_compose(self.compose)
        validate_compose(self.branch_compose)

        if data is not None:
            _add_data(self, data)

    def add_branch(self, label: Any, parent: "Tree | None" = None) -> Any:
        """
        Adds a branch to the tree and returns its key.

        >>> tree.add_branch("Names")

        :param label: String or int, one branch, returns Branch. list/tuple - each element becomes a branch, a list is returned. keys become branches (nested automatically),
                            returns a list of the created branches
        :param parent: That is, which branch to put it in.
        """
        target = parent if parent is not None else self

        if isinstance(label, dict):
            return _add_data(target, label)
        if isinstance(label, (list, tuple)):
            return [target.add_branch(item) for item in label]

        branch = Branch(label, target)
        target.children.append(branch)
        return branch

    def flush(self) -> str:
        """Returns the finished tree as a single string: markers, item text with markup and styles applied, items separated by line breaks, and cursor positioning if pos is set."""
        children = lambda t: t.children
        label = lambda t: t.label
        lines = [self.label]
        
        def walk(node: Any, prefix: str, depth: int) -> None:
            if self.max_depth is not None and depth >= self.max_depth:
                return
            kids = list(children(node))
            for i, kid in enumerate(kids):
                is_last = i == len(kids) - 1

                last, branch, space, pipe = (
                    apply_compose(attr, self.branch_compose, BaseCodes) 
                    for attr in (self.style.last, self.style.branch, self.style.space, self.style.pipe)
                )

                lines.append(prefix + (last if is_last else branch) + apply_compose(label(kid), self.compose, BaseCodes))
                walk(kid, prefix + (space if is_last else pipe), depth + 1)

        walk(self, "", 0)

        text = apply_compose("\n".join(lines), self.compose, BaseCodes)
        return place(f"{show_cursor()}{text}", self.pos)

    def display(self) -> Write:
        """Immediately outputs "Tree" to the terminal."""
        print(self.flush(), end="", flush=True)

    def __str__(self) -> str:
        return self.flush()

    def __call__(self) -> None:
        return self.display()
    
    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.label!r}, children={len(self.children)})"

class Branch(Tree):
    def __init__(self, label: Any, parent: Tree) -> None:
        """A Branch is a Tree that has a parent (and therefore can also call `add_branch`)."""
        super().__init__(label)
        self.parent = parent