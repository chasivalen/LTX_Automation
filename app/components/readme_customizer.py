import reflex as rx
from app.states.file_prep_state import (
    FilePrepState,
    ReadmeChoice,
)


def readme_choice_radio(
    text: str,
    value: ReadmeChoice,
    current_choice: rx.Var[ReadmeChoice | None],
) -> rx.Component:
    """Helper to create a radio button for Read Me choice."""
    return rx.el.label(
        rx.el.input(
            type="radio",
            name="readme_choice",
            checked=current_choice == value,
            on_change=lambda: FilePrepState.set_readme_choice(
                value
            ),
            class_name="mr-2 accent-blue-600",
            default_value=value,
        ),
        rx.el.span(text, class_name="text-gray-700"),
        class_name="flex items-center mb-2 cursor-pointer hover:bg-gray-100 p-1 rounded",
    )


def readme_customizer_component() -> rx.Component:
    """Component for customizing the Read Me instructions."""
    return rx.el.div(
        rx.el.h4(
            "Customize Evaluator Instructions (Read Me)",
            class_name="text-xl font-medium mb-4 text-gray-700",
        ),
        rx.el.details(
            rx.el.summary(
                "View/Hide Default Instructions",
                class_name="cursor-pointer font-medium text-blue-600 hover:text-blue-800 mb-2 outline-none focus:ring-2 focus:ring-blue-300 rounded px-1",
            ),
            rx.el.div(
                rx.markdown(FilePrepState.default_readme),
                class_name="prose prose-sm max-w-none p-3 border border-gray-200 rounded bg-gray-50 max-h-60 overflow-y-auto mt-2",
            ),
            class_name="mb-6",
        ),
        rx.el.fieldset(
            rx.el.legend(
                "Choose Instruction Method:",
                class_name="text-lg font-medium mb-3 text-gray-600",
            ),
            readme_choice_radio(
                "Use Default Instructions",
                "default",
                FilePrepState.readme_choice,
            ),
            readme_choice_radio(
                "Customize Default Instructions",
                "customize",
                FilePrepState.readme_choice,
            ),
            readme_choice_radio(
                "Create New Instructions From Scratch",
                "new",
                FilePrepState.readme_choice,
            ),
            class_name="mb-6 border border-gray-200 p-4 rounded bg-white",
        ),
        rx.match(
            FilePrepState.readme_choice,
            (
                "customize",
                rx.el.div(
                    rx.el.h5(
                        "Edit Instructions (Markdown Supported):",
                        class_name="text-lg font-medium mb-2 text-gray-600",
                    ),
                    rx.el.textarea(
                        default_value=FilePrepState.custom_readme_content,
                        on_change=FilePrepState.set_custom_readme_content.debounce(
                            300
                        ),
                        placeholder="Enter markdown content here...",
                        class_name="w-full p-2 border border-gray-300 rounded shadow-sm min-h-[300px] focus:outline-none focus:ring-2 focus:ring-blue-500",
                    ),
                    class_name="mb-6",
                ),
            ),
            (
                "new",
                rx.el.div(
                    rx.el.h5(
                        "Create New Instructions (Markdown Supported):",
                        class_name="text-lg font-medium mb-2 text-gray-600",
                    ),
                    rx.el.textarea(
                        default_value=FilePrepState.custom_readme_content,
                        on_change=FilePrepState.set_custom_readme_content.debounce(
                            300
                        ),
                        placeholder="Enter markdown content here...",
                        class_name="w-full p-2 border border-gray-300 rounded shadow-sm min-h-[300px] focus:outline-none focus:ring-2 focus:ring-blue-500",
                    ),
                    class_name="mb-6",
                ),
            ),
            rx.fragment(),
        ),
        rx.el.div(
            rx.el.button(
                "⬅ Edit MT Engines",
                on_click=lambda: FilePrepState.set_engines_confirmed(
                    False
                ),
                class_name="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 transition duration-150",
            ),
            rx.el.button(
                "Confirm Instructions ➡",
                on_click=FilePrepState.confirm_readme,
                disabled=FilePrepState.is_confirm_readme_disabled,
                class_name="px-6 py-3 bg-blue-600 text-white rounded-lg shadow font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition duration-150",
            ),
            class_name="flex justify-between items-center mt-6 border-t border-gray-200 pt-4",
        ),
        class_name="p-4 border border-gray-200 rounded-lg bg-gray-50 shadow",
    )