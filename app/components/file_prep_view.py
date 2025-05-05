import reflex as rx
from app.states.app_state import AppState, ProjectType
from app.states.file_prep_state import FilePrepState
from app.components.language_pair_selector import (
    language_pair_selector,
)
from app.components.engine_selector import (
    engine_selector_component,
)
from app.components.readme_customizer import (
    readme_customizer_component,
)
from app.components.stakeholder_perspective import (
    stakeholder_perspective_component,
)


def project_type_button(text: ProjectType) -> rx.Component:
    """Helper function to create a project type selection button."""
    return rx.el.button(
        text,
        on_click=lambda: AppState.set_file_prep_project_type(
            text
        ),
        class_name=rx.cond(
            AppState.file_prep_project_type == text,
            "px-6 py-3 bg-blue-600 text-white rounded-lg shadow font-medium transition duration-150",
            "px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium transition duration-150",
        ),
    )


def mt_project_view() -> rx.Component:
    """The view for MT projects, progressing through pairs, engines, Read Me, and Stakeholder comments."""
    return rx.match(
        FilePrepState.pairs_confirmed,
        (False, language_pair_selector()),
        (
            True,
            rx.match(
                FilePrepState.engines_confirmed,
                (False, engine_selector_component()),
                (
                    True,
                    rx.match(
                        FilePrepState.readme_confirmed,
                        (
                            False,
                            readme_customizer_component(),
                        ),
                        (
                            True,
                            rx.match(
                                FilePrepState.stakeholder_confirmed,
                                (
                                    False,
                                    stakeholder_perspective_component(),
                                ),
                                (
                                    True,
                                    rx.el.div(
                                        rx.el.h4(
                                            "MT Project - Configuration Complete 🎉",
                                            class_name="text-xl font-medium mb-4 text-green-700",
                                        ),
                                        rx.el.p(
                                            "Language pairs, MT engines, Read Me instructions, and stakeholder comments have been set.",
                                            class_name="text-gray-600 mb-4",
                                        ),
                                        rx.el.details(
                                            rx.el.summary(
                                                "View Final Read Me Content",
                                                class_name="cursor-pointer font-medium text-blue-600 hover:text-blue-800 mb-2 outline-none focus:ring-2 focus:ring-blue-300 rounded px-1",
                                            ),
                                            rx.el.div(
                                                rx.markdown(
                                                    FilePrepState.final_readme_content
                                                ),
                                                class_name="prose prose-sm max-w-none p-3 border border-gray-200 rounded bg-gray-50 max-h-60 overflow-y-auto mt-2",
                                            ),
                                            class_name="mb-4",
                                        ),
                                        rx.el.details(
                                            rx.el.summary(
                                                "View Stakeholder Comments",
                                                class_name="cursor-pointer font-medium text-blue-600 hover:text-blue-800 mb-2 outline-none focus:ring-2 focus:ring-blue-300 rounded px-1",
                                            ),
                                            rx.el.div(
                                                rx.text(
                                                    FilePrepState.stakeholder_comments,
                                                    class_name=rx.cond(
                                                        FilePrepState.stakeholder_comments.length()
                                                        > 0,
                                                        "whitespace-pre-wrap",
                                                        "text-gray-500 italic",
                                                    ),
                                                ),
                                                class_name="text-sm p-3 border border-gray-200 rounded bg-gray-50 max-h-40 overflow-y-auto mt-2",
                                            ),
                                            class_name="mb-6",
                                        ),
                                        rx.el.p(
                                            "Next Step: Define Metrics and Weights.",
                                            class_name="text-gray-600 italic font-semibold mb-6",
                                        ),
                                        rx.el.div(
                                            rx.el.button(
                                                "Edit Language Pairs",
                                                on_click=lambda: FilePrepState.set_pairs_confirmed(
                                                    False
                                                ),
                                                class_name="mr-4 mb-2 px-4 py-2 text-sm bg-yellow-500 text-white rounded hover:bg-yellow-600 transition duration-150",
                                            ),
                                            rx.el.button(
                                                "Edit MT Engines",
                                                on_click=lambda: FilePrepState.set_engines_confirmed(
                                                    False
                                                ),
                                                class_name="mr-4 mb-2 px-4 py-2 text-sm bg-yellow-500 text-white rounded hover:bg-yellow-600 transition duration-150",
                                            ),
                                            rx.el.button(
                                                "Edit Read Me",
                                                on_click=lambda: FilePrepState.set_readme_confirmed(
                                                    False
                                                ),
                                                class_name="mr-4 mb-2 px-4 py-2 text-sm bg-yellow-500 text-white rounded hover:bg-yellow-600 transition duration-150",
                                            ),
                                            rx.el.button(
                                                "Edit Stakeholder Perspective",
                                                on_click=lambda: FilePrepState.set_stakeholder_confirmed(
                                                    False
                                                ),
                                                class_name="mb-2 px-4 py-2 text-sm bg-yellow-500 text-white rounded hover:bg-yellow-600 transition duration-150",
                                            ),
                                            class_name="flex flex-wrap border-t border-gray-200 pt-4",
                                        ),
                                        class_name="p-6 border border-green-200 rounded-lg bg-green-50 shadow-md",
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
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
            class_name="flex flex-wrap gap-4 mb-8",
        ),
        rx.match(
            AppState.file_prep_project_type,
            ("MT", mt_project_view()),
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