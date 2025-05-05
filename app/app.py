"""LTX Automation App"""

import reflex as rx
from app.components.project_selection import (
    project_selection_component,
)
from app.components.main_interface import (
    main_interface_component,
)
from app.states.app_state import AppState
from app.states.project_state import ProjectState


def index() -> rx.Component:
    """The main page of the app."""
    return rx.el.div(
        rx.el.h1(
            "LTX Automation",
            class_name="text-4xl font-bold text-center my-8 text-gray-900",
        ),
        rx.cond(
            AppState.project_selected,
            main_interface_component(),
            project_selection_component(),
        ),
        class_name="min-h-screen bg-gray-50",
    )


app = rx.App(
    theme=rx.theme(appearance="light"), stylesheets=[]
)
app.add_page(index)