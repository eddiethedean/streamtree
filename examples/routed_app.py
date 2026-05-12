"""Multi-page demo: query-param routing + optional Pydantic JSON form."""

from __future__ import annotations

import json

from pydantic import BaseModel, ValidationError

from streamtree import component, render
from streamtree.elements import Button, Form, Markdown, Page, Routes, Text, TextInput, Title, VStack
from streamtree.forms import format_validation_errors, model_validate_json
from streamtree.routing import set_route
from streamtree.state import form_state, state


class Profile(BaseModel):
    name: str
    email: str


@component
def ProfileForm() -> object:
    raw = form_state('{"name":"","email":""}', key="profile_json")
    err = state("", key="profile_err")

    def submit() -> None:
        try:
            model_validate_json(Profile, raw.edit_value())
            err.set("")
            raw.commit()
        except (ValidationError, json.JSONDecodeError, TypeError) as e:
            if isinstance(e, ValidationError):
                err.set(format_validation_errors(e))
            else:
                err.set(str(e))

    return Form(
        Title("Profile (JSON)"),
        TextInput("JSON payload", value=raw),
        Markdown(err() or " "),
        Button("Validate & commit", submit=True, on_click=submit),
        form_key="profile_form",
    )


@component
def Nav() -> object:
    return VStack(
        Text("Pages use query param `route`:"),
        Button("Home", on_click=lambda: set_route("home")),
        Button("Profile", on_click=lambda: set_route("profile")),
    )


@component
def App() -> object:
    return Page(
        Nav(),
        Routes(
            routes=(
                ("home", VStack(Title("Home"), Text("Open Profile to try Pydantic JSON validation."))),
                ("profile", ProfileForm()),
            ),
            default="home",
        ),
    )


if __name__ == "__main__":
    render(App())
