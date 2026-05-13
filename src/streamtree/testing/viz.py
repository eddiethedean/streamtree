"""Human-readable views of :func:`~streamtree.testing.render_to_tree` output."""

from __future__ import annotations

import re
from typing import Any


def _escape_mermaid_label(text: str) -> str:
    t = text.replace('"', "#quot;")
    return re.sub(r"[\[\]{}]", "", t)


def format_tree_text(
    node: dict[str, Any] | list[Any], *, indent: str = "  ", depth: int = 0
) -> str:
    """Render a ``render_to_tree`` dict (or JSON-equivalent) as an indented outline."""
    if isinstance(node, list):
        parts = [format_tree_text(item, indent=indent, depth=depth) for item in node]
        return "\n".join(p for p in parts if p)
    if not isinstance(node, dict):
        return ""
    prefix = indent * depth
    kind = str(node.get("kind", "?"))
    key = node.get("key")
    extra: list[str] = []
    if "label" in node and isinstance(node["label"], str):
        extra.append(f"label={node['label']!r}")
    if "name" in node and isinstance(node["name"], str):
        extra.append(f"name={node['name']!r}")
    bits = [kind]
    if key is not None:
        bits.append(f"key={key!r}")
    bits.extend(extra)
    lines = [f"{prefix}{' '.join(bits)}"]
    if isinstance(node.get("child"), dict):
        sub = format_tree_text(node["child"], indent=indent, depth=depth + 1)
        if sub:
            lines.append(sub)
    if isinstance(node.get("fallback"), dict):
        lines.append(f"{prefix}{indent}fallback")
        sub = format_tree_text(node["fallback"], indent=indent, depth=depth + 2)
        if sub:
            lines.append(sub)
    for ch in node.get("children") or []:
        if isinstance(ch, dict):
            sub = format_tree_text(ch, indent=indent, depth=depth + 1)
            if sub:
                lines.append(sub)
    tabs = node.get("tabs")
    if isinstance(tabs, list):
        for tab in tabs:
            if isinstance(tab, dict) and isinstance(tab.get("child"), dict):
                title = tab.get("title", "")
                lines.append(f"{prefix}{indent}tab {title!r}")
                sub = format_tree_text(tab["child"], indent=indent, depth=depth + 2)
                if sub:
                    lines.append(sub)
    for side in ("narrow", "main"):
        if isinstance(node.get(side), dict):
            lines.append(f"{prefix}{indent}{side}")
            sub = format_tree_text(node[side], indent=indent, depth=depth + 2)
            if sub:
                lines.append(sub)
    return "\n".join(lines)


def tree_dict_to_mermaid(node: dict[str, Any] | list[Any]) -> str:
    """Build a Mermaid ``flowchart TD`` diagram from a ``render_to_tree`` dict.

    Large trees and duplicate ``kind`` labels can make diagrams noisy; prefer
    :func:`format_tree_text` or JSON snapshots for dense UIs.
    """
    out_lines = ["flowchart TD"]
    counter = 0

    def next_id() -> str:
        nonlocal counter
        nid = f"n{counter}"
        counter += 1
        return nid

    def walk(n: dict[str, Any] | list[Any], parent: str | None) -> None:
        if isinstance(n, list):
            for item in n:
                walk(item, parent)
            return
        if not isinstance(n, dict):
            return
        nid = next_id()
        kind = _escape_mermaid_label(str(n.get("kind", "?")))
        key = n.get("key")
        label = kind if key is None else f"{kind} | k={_escape_mermaid_label(repr(key))}"
        out_lines.append(f'  {nid}["{label}"]')
        if parent is not None:
            out_lines.append(f"  {parent} --> {nid}")
        cur = nid
        if isinstance(n.get("child"), dict):
            walk(n["child"], cur)
        if isinstance(n.get("fallback"), dict):
            walk(n["fallback"], cur)
        for ch in n.get("children") or []:
            walk(ch, cur)
        tabs = n.get("tabs")
        if isinstance(tabs, list):
            for tab in tabs:
                if isinstance(tab, dict) and isinstance(tab.get("child"), dict):
                    walk(tab["child"], cur)
        for side in ("narrow", "main"):
            if isinstance(n.get(side), dict):
                walk(n[side], cur)

    walk(node, None)
    return "\n".join(out_lines)


__all__ = ["format_tree_text", "tree_dict_to_mermaid"]
