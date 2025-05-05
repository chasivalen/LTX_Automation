"""LTX Automation App"""

import reflex as rx
from app.states.app_state import AppState
from app.states.project_state import ProjectState
from app.states.file_prep_state import FilePrepState
from app.components.initial_selection import (
    initial_selection_component,
)
from app.components.project_selection import (
    project_selection_component,
)
from app.components.main_interface import (
    main_interface_component,
    placeholder_view,
)
from app.components.sidebar import sidebar
from app.components.header import header_component


def seo_view_component() -> rx.Component:
    """The view shown when SEO is selected initially."""
    return rx.el.div(
        placeholder_view("SEO Automation"),
        class_name="p-6 flex justify-center items-start min-h-[calc(100vh-4rem)]",
    )


def ltx_bench_view_component() -> rx.Component:
    """The view structure for the LTX Bench workflow."""
    return rx.cond(
        AppState.project_selected,
        rx.el.div(
            sidebar(),
            rx.el.main(
                main_interface_component(),
                class_name="ml-64 flex-grow",
            ),
            class_name="flex min-h-[calc(100vh-4rem)]",
        ),
        rx.el.div(
            project_selection_component(),
            class_name="flex justify-center items-center min-h-[calc(100vh-4rem)]",
        ),
    )


def index() -> rx.Component:
    """The main page of the app."""
    return rx.el.div(
        header_component(),
        rx.el.div(
            rx.match(
                AppState.initial_choice,
                ("SEO", seo_view_component()),
                ("LTX Bench", ltx_bench_view_component()),
                rx.el.div(
                    initial_selection_component(),
                    class_name="flex justify-center items-center min-h-[calc(100vh-4rem)]",
                ),
            ),
            class_name="pt-16",
        ),
        class_name="min-h-screen bg-gray-50",
    )


app = rx.App(
    theme=rx.theme(appearance="light"), stylesheets=[]
)
app.add_page(index)