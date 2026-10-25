"""

Chromite/tree.py
~~~~~~~~~~~~~~~~
Creating trees.

Copyright (C) 2026 NastyaNoTamashii.
License: MIT
Author: NastyaNoTamashii

"""

from __future__ import annotations

__all__ = ['Tree', 'TreeStyle', 'Branch']

from typing import Any, Optional
from dataclasses import dataclass, replace
from .terminal import place
from .codes import validate_compose, apply_compose
from ._base import Renderable
from ._types import StyleType, PosType

def _add_data(parent: Tree, data: dict | list | tuple) -> list[Branch]:
    """Convert a dict/list into nested branches within a parent element."""
    items = data.items() if isinstance(data, dict) else enumerate(data)
    created: list[Branch] = []
    for key, value in items:
        if isinstance(value, (dict, list, tuple)) and value:
            branch = parent.add_branch(str(key))
            _add_data(branch, value)
        elif isinstance(data, dict):
            branch = parent.add_branch(f"{key}: {value}")  # the key is not lost
        else:
            branch = parent.add_branch(str(value))
        created.append(branch)
    return created

# Table styles
@dataclass(frozen=True)
class _Style:
    branch: str = "├── "
    last: str =   "└── "
    pipe: str =   "│   "
    space: str =  "    "
    
    def copy(self, **changes) -> "TreeStyle":
        """Copy the style with changes: ROUNDED.copy(h="=")"""
        return replace(self, **changes)

class TreeStyle:
    """Different tree styles: Single, Rounded"""
    Single = _Style()
    Rounded = _Style(last="╰── ")

class Tree(Renderable):
    __slots__ = ("label", "style", "compose", "branch_compose", "pos", "max_depth", "children",)

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
        """Returns the finished tree as a single string, with styles applied and cursor positioning if pos is set."""
        lines = [apply_compose(self.label, self.compose)]
        last, branch, space, pipe = (
            apply_compose(attr, self.branch_compose)
            for attr in (self.style.last, self.style.branch, self.style.space, self.style.pipe)
        )

        def walk(node: Tree, prefix: str, depth: int) -> None:
            if self.max_depth is not None and depth >= self.max_depth:
                return
            for i, kid in enumerate(node.children):
                is_last = i == len(node.children) - 1
                lines.append(prefix + (last if is_last else branch) + apply_compose(kid.label, self.compose))
                walk(kid, prefix + (space if is_last else pipe), depth + 1)

        walk(self, "", 0)
        return place("\n".join(lines), self.pos)
    
    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.label!r}, children={len(self.children)})"

class Branch(Tree):
    __slots__ = ("parent",)

    def __init__(self, label: Any, parent: Tree) -> None:
        """A Branch is a Tree that has a parent (and therefore can also call `add_branch`)."""
        super().__init__(label)
        self.parent = parent