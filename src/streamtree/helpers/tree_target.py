"""Resolve ``module:attr`` targets for ``streamtree tree`` and related tooling."""

from __future__ import annotations

import importlib
from typing import Any

from streamtree.core.element import Element


def load_element_from_target(spec: str) -> Element:
    """Import ``module`` and resolve ``attr`` to an :class:`~streamtree.core.element.Element`.

    ``spec`` must be ``dotted.module.path:attribute`` where ``attribute`` is either an
    :class:`~streamtree.core.element.Element` instance or a zero-argument callable returning one.
    """
    if ":" not in spec:
        msg = "Expected ``module:attr`` (for example ``myapp.trees:build_root``)."
        raise ValueError(msg)
    mod_name, attr_name = spec.split(":", 1)
    mod_name, attr_name = mod_name.strip(), attr_name.strip()
    if not mod_name or not attr_name:
        msg = "Expected ``module:attr`` with non-empty module and attribute names."
        raise ValueError(msg)
    try:
        module = importlib.import_module(mod_name)
    except ModuleNotFoundError as exc:
        msg = f"Could not import module {mod_name!r}: {exc}"
        raise ValueError(msg) from exc
    try:
        obj: Any = getattr(module, attr_name)
    except AttributeError as exc:
        msg = f"Module {mod_name!r} has no attribute {attr_name!r}."
        raise ValueError(msg) from exc
    if callable(obj):
        root = obj()
    else:
        root = obj
    if not isinstance(root, Element):
        msg = f"Resolved object is not an Element (got {type(root)!r})."
        raise TypeError(msg)
    return root
