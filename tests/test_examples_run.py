"""Smoke-test every example script with ``streamlit.testing.v1.AppTest``.

Streamlit surfaces script errors on ``at.exception`` (often without raising from
``.run()``), so we assert ``len(at.exception) == 0``.

``echarts_demo.py`` is skipped: ``streamlit-echarts`` registers a v2 custom
component that raises ``StreamlitAPIException`` in the AppTest harness
(file-backed JS / pyproject declaration path).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

_EXAMPLES = Path(__file__).resolve().parent.parent / "examples"

_APPTEST_SKIP: dict[str, str] = {
    "echarts_demo.py": (
        "streamlit-echarts custom component fails AppTest registration "
        "(StreamlitAPIException: file-backed js / pyproject component declaration)."
    ),
}


def _example_scripts() -> list[Path]:
    root = sorted(_EXAMPLES.glob("*.py"))
    pages = sorted((_EXAMPLES / "pages").glob("*.py"))
    return [p for p in (*root, *pages) if p.name != "__init__.py"]


_EXAMPLE_SCRIPTS = _example_scripts()
_EXAMPLE_IDS = [str(p.relative_to(_EXAMPLES.parent)) for p in _EXAMPLE_SCRIPTS]


@pytest.mark.parametrize("script", _EXAMPLE_SCRIPTS, ids=_EXAMPLE_IDS)
def test_example_app_test_no_exceptions(script: Path) -> None:
    skip = _APPTEST_SKIP.get(script.name)
    if skip is not None:
        pytest.skip(skip)
    at = AppTest.from_file(str(script.resolve())).run(timeout=90)
    assert len(at.exception) == 0, (
        f"{script.relative_to(_EXAMPLES.parent)}: AppTest reported "
        f"{len(at.exception)} exception(s); first: {at.exception[0].message[:800]!r}"
    )
