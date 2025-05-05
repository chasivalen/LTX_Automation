"""LTX Automation App"""

import reflex as rx
from app.components.project_selection import (
    project_selection_component,
)
from app.components.main_interface import (
    main_interface_component,
)
from app.components.sidebar import sidebar
from app.states.app_state import AppState
from app.states.project_state import ProjectState


def index() -> rx.Component:
    """The main page of the app."""
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "LTX Automation",
                class_name="text-3xl font-bold text-gray-900",
            ),
            rx.el.p(
                f"Project: {ProjectState.selected_project}",
                class_name=rx.cond(
                    AppState.project_selected,
                    "text-sm text-gray-600",
                    "hidden",
                ),
            ),
            class_name="fixed top-0 left-0 right-0 h-16 px-6 flex items-center justify-between bg-white border-b border-gray-200 z-10",
        ),
        rx.el.div(
            rx.cond(
                AppState.project_selected,
                rx.el.div(
                    sidebar(),
                    rx.el.main(
                        main_interface_component(),
                        class_name="ml-64 flex-grow",
                    ),
                    class_name="flex min-h-screen pt-16",
                ),
                rx.el.div(
                    project_selection_component(),
                    class_name="pt-16 flex justify-center items-center min-h-screen",
                ),
            ),
            class_name="w-full",
        ),
        class_name="min-h-screen bg-gray-50 relative",
    )


app = rx.App(
    theme=rx.theme(appearance="light"), stylesheets=[]
)
app.add_page(index)