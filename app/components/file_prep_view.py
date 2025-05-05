import reflex as rx
from app.states.app_state import AppState, ProjectType


def project_type_button(text: ProjectType) -> rx.Component:
    """Helper function to create a project type selection button."""
    return rx.el.button(
        text,
        on_click=lambda: AppState.set_file_prep_project_type(
            text
        ),
        class_name=rx.cond(
            AppState.file_prep_project_type == text,
            "px-6 py-3 bg-blue-600 text-white rounded-lg shadow font-medium",
            "px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium",
        ),
    )


def file_prep_view() -> rx.Component:
    """The view displayed when 'File Prep' is selected within LTX Bench."""
    return rx.el.div(
        rx.el.h3(
            "File Prep: Select Project Type",
            class_name="text-2xl font-semibold mb-6 text-gray-800",
        ),
        rx.el.div(
            project_type_button("MT"),
            project_type_button("LLM"),
            project_type_button("Gen AI"),
            class_name="flex space-x-4 mb-8",
        ),
        rx.match(
            AppState.file_prep_project_type,
            (
                "MT",
                rx.el.div(
                    rx.el.h4(
                        "MT Project Options",
                        class_name="text-xl font-medium mb-4 text-gray-700",
                    ),
                    rx.el.p(
                        "Placeholder for Machine Translation specific file preparation steps.",
                        class_name="text-gray-600",
                    ),
                    class_name="p-4 border border-gray-200 rounded-lg bg-gray-50",
                ),
            ),
            (
                "LLM",
                rx.el.div(
                    rx.el.h4(
                        "LLM Project Options",
                        class_name="text-xl font-medium mb-4 text-gray-700",
                    ),
                    rx.el.p(
                        "Placeholder for Large Language Model specific file preparation steps.",
                        class_name="text-gray-600",
                    ),
                    class_name="p-4 border border-gray-200 rounded-lg bg-gray-50",
                ),
            ),
            (
                "Gen AI",
                rx.el.div(
                    rx.el.h4(
                        "Gen AI Project Options",
                        class_name="text-xl font-medium mb-4 text-gray-700",
                    ),
                    rx.el.p(
                        "Placeholder for Generative AI specific file preparation steps.",
                        class_name="text-gray-600",
                    ),
                    class_name="p-4 border border-gray-200 rounded-lg bg-gray-50",
                ),
            ),
            rx.el.p(
                "Please select a project type above to see relevant options.",
                class_name="text-gray-500 italic",
            ),
        ),
        class_name="p-6",
    )