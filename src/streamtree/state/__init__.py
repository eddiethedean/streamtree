"""Session-backed reactive values."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, cast

import streamlit as st

from streamtree.core.context import current_context

T = TypeVar("T")


def _allocate_state_key(explicit: str | None) -> str:
    if explicit:
        return f"streamtree.state.{explicit}"
    ctx = current_context()
    idx = ctx.next_anonymous_index()
    return f"streamtree.{ctx.path()}.s{idx}"


@dataclass
class StateVar(Generic[T]):
    """Read/write view backed by ``st.session_state``."""

    _key: str
    _default: T

    def __call__(self) -> T:
        if self._key not in st.session_state:
            st.session_state[self._key] = self._default
        return cast(T, st.session_state[self._key])

    def set(self, value: T) -> None:
        st.session_state[self._key] = value

    def update(self, fn: Callable[[T], T]) -> None:
        st.session_state[self._key] = fn(cast(T, st.session_state[self._key]))

    def increment(self, delta: int = 1) -> None:
        """Add ``delta`` to numeric state; re-seeds from the initial default if the key was removed."""
        if self._key not in st.session_state:
            st.session_state[self._key] = self._default
        cur = cast(T, st.session_state[self._key])
        if not isinstance(cur, (int, float)):
            raise TypeError("increment() requires numeric state")
        st.session_state[self._key] = cur + delta  # type: ignore[assignment,operator]

    @property
    def key(self) -> str:
        return self._key


def state(initial: T, *, key: str | None = None) -> StateVar[T]:
    """Create or resume typed state stored in ``st.session_state``.

    Keys are scoped under the active render path unless ``key`` is explicit.
    """
    k = _allocate_state_key(key)
    if k not in st.session_state:
        st.session_state[k] = initial
    return StateVar(_key=k, _default=initial)


@dataclass
class ToggleState:
    """Boolean ``StateVar`` with an explicit ``toggle`` helper."""

    _inner: StateVar[bool]

    def __call__(self) -> bool:
        return self._inner()

    def set(self, value: bool) -> None:
        self._inner.set(value)

    def toggle(self) -> None:
        self._inner.set(not bool(self._inner()))

    @property
    def key(self) -> str:
        return self._inner.key


def toggle_state(*, key: str | None = None, initial: bool = False) -> ToggleState:
    """Boolean state with ``toggle()`` for simple flags."""
    return ToggleState(_inner=state(initial, key=key))


def session_state(key: str, *, default: Any | None = None) -> Callable[[], Any]:
    """Adopt an existing ``st.session_state`` key as a read-only callable.

    If ``default`` is ``None``, the key must already exist when ``read()`` runs
    (for example after another widget or initializer wrote it); otherwise
    :func:`read` raises :exc:`ValueError` with a short hint instead of a bare
    :exc:`KeyError`.
    """

    def read() -> Any:
        if key not in st.session_state:
            if default is not None:
                st.session_state[key] = default
            else:
                msg = (
                    f"st.session_state[{key!r}] is unset; pass default= to session_state() "
                    "when the key may be missing on first read"
                )
                raise ValueError(msg)
        return st.session_state[key]

    return read


@dataclass
class FormState(Generic[T]):
    """Pending value inside a ``Form``; committed on submit."""

    _edit_key: str
    _committed_key: str
    _default: T

    def __call__(self) -> T:
        return cast(T, st.session_state[self._committed_key])

    def edit_value(self) -> T:
        return cast(T, st.session_state[self._edit_key])

    def set_edit(self, value: T) -> None:
        st.session_state[self._edit_key] = value

    def commit(self) -> None:
        """Copy the editor buffer into the committed value (call from submit handler)."""
        st.session_state[self._committed_key] = st.session_state[self._edit_key]

    @property
    def committed_key(self) -> str:
        return self._committed_key

    @property
    def edit_key(self) -> str:
        return self._edit_key


def form_state(initial: T, *, key: str | None = None) -> FormState[T]:
    """Split editor vs committed value for ``st.form`` workflows."""
    base = _allocate_state_key(key)
    edit_key = f"{base}.edit"
    committed_key = f"{base}.committed"
    if committed_key not in st.session_state:
        st.session_state[committed_key] = initial
    if edit_key not in st.session_state:
        st.session_state[edit_key] = st.session_state[committed_key]
    return FormState(_edit_key=edit_key, _committed_key=committed_key, _default=initial)


def memo(key: str, factory: Callable[[], T]) -> T:
    """Run ``factory`` once per session for ``key`` (simple memoization).

    Storage uses ``streamtree.memo.<key>`` in ``st.session_state``. That slot is **global to
    the Streamlit session** (not namespaced by the active render path like :func:`state`).
    Choose ``key`` values that are unique across your app—e.g. prefix with an app or
    subsystem name—so unrelated components never share the same memo slot.
    """
    sk = f"streamtree.memo.{key}"
    if sk not in st.session_state:
        st.session_state[sk] = factory()
    return cast(T, st.session_state[sk])


def cache(key: str, value: T) -> T:
    """Alias of memo with a precomputed value (store if missing).

    Uses ``streamtree.cache.<key>`` in ``st.session_state`` — **session-global**, not
    render-path scoped (see :func:`memo`). Use distinct ``key`` strings to avoid collisions.
    """
    sk = f"streamtree.cache.{key}"
    if sk not in st.session_state:
        st.session_state[sk] = value
    return cast(T, st.session_state[sk])


def _deps_fingerprint(deps: tuple[Any, ...]) -> str:
    try:
        return json.dumps(deps, default=str, separators=(",", ":"), sort_keys=False)
    except TypeError:
        return repr(deps)


def memo_subtree(logical_key: str, deps: tuple[Any, ...], factory: Callable[[], T]) -> T:
    """Memoize once per session keyed by **render path**, ``logical_key``, and ``deps``.

    Unlike :func:`memo`, the slot includes :func:`streamtree.core.context.current_context`
    ``path()`` so unrelated subtrees do not share storage. Change ``deps`` when inputs
    change to invalidate the cached value.

    Session key: ``streamtree.memo_subtree.<path>.<logical_key>.<fingerprint>``.
    """
    if not isinstance(logical_key, str) or not logical_key.strip():
        raise ValueError("memo_subtree logical_key must be a non-empty string")
    ctx = current_context()
    fp = _deps_fingerprint(deps)
    sk = f"streamtree.memo_subtree.{ctx.path()}.{logical_key.strip()}.{fp}"
    if sk not in st.session_state:
        st.session_state[sk] = factory()
    return cast(T, st.session_state[sk])


__all__ = [
    "FormState",
    "StateVar",
    "ToggleState",
    "cache",
    "form_state",
    "memo",
    "memo_subtree",
    "session_state",
    "state",
    "toggle_state",
]
