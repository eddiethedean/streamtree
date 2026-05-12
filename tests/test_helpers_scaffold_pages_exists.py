"""Branch: ``pages/1_About.py`` exists before init with ``--with-pages``."""

from __future__ import annotations

import pytest

from streamtree.helpers.scaffold import write_init_project


def test_write_init_project_raises_when_about_exists_without_app(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    root = tmp_path_factory.mktemp("preabout")
    pages = root / "pages"
    pages.mkdir(parents=True)
    (pages / "1_About.py").write_text("# existing", encoding="utf-8")
    with pytest.raises(FileExistsError):
        write_init_project(root, page_title="T", with_pages=True, force=False)
