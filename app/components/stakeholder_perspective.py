import reflex as rx
from app.states.file_prep_state import FilePrepState


def stakeholder_perspective_component() -> rx.Component:
    """Component for entering stakeholder perspective comments."""
    return rx.el.div(
        rx.el.h4(
            "Stakeholder's Perspective",
            class_name="text-xl font-medium mb-4 text-gray-700",
        ),
        rx.el.p(
            "Enter any comments or context provided by the stakeholders regarding this evaluation.",
            class_name="text-sm text-gray-600 mb-4",
        ),
        rx.el.textarea(
            default_value=FilePrepState.stakeholder_comments,
            on_change=FilePrepState.set_stakeholder_comments.debounce(
                300
            ),
            placeholder="Enter comments here...",
            class_name="w-full p-3 border border-gray-300 rounded shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[150px] mb-6",
        ),
        rx.el.div(
            rx.el.button(
                "⬅ Edit Read Me",
                on_click=lambda: FilePrepState.set_readme_confirmed(
                    False
                ),
                class_name="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 transition duration-150",
            ),
            rx.el.button(
                "Confirm Perspective & Define Metrics ➡",
                on_click=FilePrepState.confirm_stakeholder_perspective,
                disabled=FilePrepState.is_confirm_stakeholder_disabled,
                class_name="px-6 py-3 bg-blue-600 text-white rounded-lg shadow font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition duration-150",
            ),
            class_name="flex justify-between items-center mt-6 border-t border-gray-200 pt-4",
        ),
        class_name="p-4 border border-gray-200 rounded-lg bg-gray-50 shadow",
    )