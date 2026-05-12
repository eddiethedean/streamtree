"""Pydantic model bound to ``TextInput`` widgets via ``str_text_inputs``."""

from __future__ import annotations

import json

from pydantic import BaseModel, ValidationError

from streamtree import component
from streamtree.app import App
from streamtree.app_context import provider
from streamtree.core.component import render_app
from streamtree.elements import Button, Markdown, Text, ThemeRoot, VStack
from streamtree.forms import (
    bind_str_fields,
    format_validation_errors,
    model_validate_json,
    str_text_inputs,
)
from streamtree.state import state
from streamtree.theme import Theme


class Contact(BaseModel):
    name: str
    email: str


@component
def ContactForm() -> object:
    fields = bind_str_fields(Contact, key_prefix="contact_form")
    err = state("", key="contact_form_err")

    def validate_json() -> None:
        try:
            payload = {k: fields[k]() for k in fields}
            model_validate_json(Contact, json.dumps(payload))
            err.set("")
        except ValidationError as e:
            err.set(format_validation_errors(e))
        except (TypeError, ValueError) as e:
            err.set(str(e))

    return VStack(
        ThemeRoot(),
        *str_text_inputs(
            Contact, bindings=fields, field_labels={"name": "Full name", "email": "Email"}
        ),
        Button("Validate JSON shape", on_click=validate_json),
        Markdown(err() or " "),
    )


if __name__ == "__main__":
    t = Theme(primary_color="#0068c9", custom_css="a { color: var(--st-theme-primary); }\n")
    with provider(theme=t):
        render_app(
            App(
                page_title="Model form",
                body=VStack(Text("Declarative str fields + Pydantic"), ContactForm()),
            )
        )
