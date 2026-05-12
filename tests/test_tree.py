from __future__ import annotations

from streamtree.core import component, fragment
from streamtree.elements import Button, Card, Page, Text, VStack
from streamtree.testing import render_to_tree


@component
def Sample():
    return Card(Text("hi"), Button("go", key="btn"))


def test_render_to_tree_serializes_component_call() -> None:
    tree = render_to_tree(Page(Sample()))
    assert tree["kind"] == "Page"
    assert tree["children"][0]["kind"] == "ComponentCall"
    assert tree["children"][0]["name"] == "Sample"


def test_fragment_normalization() -> None:
    inner = fragment(Text("a"), Text("b"))
    tree = render_to_tree(VStack(inner))
    assert tree["kind"] == "VStack"
    assert tree["children"][0]["kind"] == "Fragment"
    assert len(tree["children"][0]["children"]) == 2
