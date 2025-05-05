import reflex as rx
from app.states.project_state import ProjectState
from app.states.app_state import AppState
from app.components.file_prep_view import file_prep_view


def default_view() -> rx.Component:
    """The default view shown when a project is selected but no specific task."""
    return rx.el.div(
        rx.el.h3(
            "Welcome to your Project",
            class_name="text-2xl font-semibold mb-4 text-gray-800",
        ),
        rx.el.p(
            f"Project '{ProjectState.selected_project}' is selected.",
            class_name="text-gray-600 mb-2",
        ),
        rx.el.p(
            "Please select an option from the sidebar to begin.",
            class_name="text-gray-600",
        ),
        class_name="p-6",
    )


def placeholder_view(title: str) -> rx.Component:
    """A generic placeholder view."""
    return rx.el.div(
        rx.el.h3(
            title,
            class_name="text-2xl font-semibold mb-4 text-gray-800",
        ),
        rx.el.p(
            f"Placeholder content for {title}.",
            class_name="text-gray-600",
        ),
        class_name="p-6",
    )


def main_interface_component() -> rx.Component:
    """Component displaying the main content based on sidebar selection."""
    return rx.el.div(
        rx.match(
            AppState.selected_view,
            ("default", default_view()),
            ("file_prep", file_prep_view()),
            (
                "final_file_prep",
                placeholder_view("Final File Prep"),
            ),
            (
                "update_tableau",
                placeholder_view("Update Tableau"),
            ),
            (
                "seo_automation",
                placeholder_view("SEO Automation"),
            ),
            default_view(),
        ),
        class_name="flex-grow p-6",
    )