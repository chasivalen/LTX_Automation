import reflex as rx
from app.states.app_state import AppState


def sidebar_link(text: str, view: str) -> rx.Component:
    """Helper function to create a sidebar link."""
    return rx.el.li(
        rx.el.button(
            text,
            on_click=lambda: AppState.set_selected_view(
                view
            ),
            class_name=rx.cond(
                AppState.selected_view == view,
                "w-full text-left px-4 py-2 bg-blue-100 text-blue-700 rounded border border-blue-300 font-semibold",
                "w-full text-left px-4 py-2 hover:bg-gray-100 rounded border border-transparent text-gray-600 hover:text-gray-900",
            ),
        ),
        class_name="mb-1",
    )


def sidebar() -> rx.Component:
    """The sidebar component for LTX Bench navigation."""
    return rx.el.div(
        rx.el.h4(
            "LTX Bench Menu",
            class_name="text-lg font-semibold mb-3 text-gray-800 px-4 pt-4",
        ),
        rx.el.ul(
            sidebar_link("File Prep", "file_prep"),
            sidebar_link("Final Report", "final_file_prep"),
            sidebar_link(
                "Update Tableau", "update_tableau"
            ),
            class_name="list-none p-0 px-2",
        ),
        rx.el.div(
            rx.el.button(
                "Change Project",
                on_click=lambda: AppState.set_project_selected(
                    False
                ),
                class_name="mb-2 w-full px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600",
            ),
            rx.el.button(
                "Change Mode (SEO/LTX)",
                on_click=AppState.reset_initial_choice,
                class_name="w-full px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600",
            ),
            class_name="mt-auto px-4 pb-4 pt-2 border-t border-gray-200",
        ),
        class_name="w-64 h-full bg-white border-r border-gray-200 flex flex-col fixed top-0 left-0 pt-16",
    )