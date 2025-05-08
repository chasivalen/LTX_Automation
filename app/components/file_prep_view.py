import reflex as rx
from app.states.app_state import AppState, ProjectType
from app.states.file_prep_state import (
    FilePrepState,
    MAX_PREVIEW_ROWS,
)
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
from app.components.metric_definition import (
    metric_definition_component,
)
from app.components.column_definition import (
    column_definition_component,
)
from app.components.template_uploader import (
    template_uploader_component,
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


def _preview_table_component() -> rx.Component:
    """Displays a preview of the uploaded data."""
    return rx.el.div(
        rx.el.h5(
            "Data Preview (First "
            + str(MAX_PREVIEW_ROWS)
            + " Rows)",
            class_name="text-lg font-medium mb-2 text-gray-700",
        ),
        rx.cond(
            FilePrepState.preview_table_data.length() > 0,
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.foreach(
                                FilePrepState.preview_table_headers,
                                lambda header: rx.el.th(
                                    header,
                                    class_name="p-2 border-b border-gray-300 text-left text-sm font-semibold text-gray-600 bg-gray-100",
                                ),
                            )
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            FilePrepState.preview_table_data,
                            lambda row_data: rx.el.tr(
                                rx.foreach(
                                    FilePrepState.preview_table_headers,
                                    lambda header_key: rx.el.td(
                                        row_data.get(
                                            header_key, ""
                                        ),
                                        class_name="p-2 border-b border-gray-200 text-sm text-gray-700",
                                    ),
                                )
                            ),
                        )
                    ),
                    class_name="w-full border-collapse border border-gray-200 rounded-md shadow-sm",
                ),
                class_name="overflow-x-auto max-h-96",
            ),
            rx.el.p(
                "No data to preview or files not yet processed for preview.",
                class_name="text-gray-500 italic",
            ),
        ),
        class_name="my-6 p-4 border border-gray-200 rounded-lg bg-white",
    )


def mt_project_view() -> rx.Component:
    """The view for MT projects, progressing through various configuration steps."""
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
                                    rx.match(
                                        FilePrepState.metrics_confirmed,
                                        (
                                            False,
                                            metric_definition_component(),
                                        ),
                                        (
                                            True,
                                            rx.match(
                                                FilePrepState.column_structure_finalized,
                                                (
                                                    False,
                                                    column_definition_component(),
                                                ),
                                                (
                                                    True,
                                                    rx.match(
                                                        FilePrepState.template_preview_ready,
                                                        (
                                                            False,
                                                            template_uploader_component(),
                                                        ),
                                                        (
                                                            True,
                                                            rx.el.div(
                                                                rx.el.h4(
                                                                    "MT Project - Configuration & Preview",
                                                                    class_name="text-xl font-medium mb-4 text-green-700",
                                                                ),
                                                                rx.el.p(
                                                                    "All steps completed. Review the final configuration and data preview below.",
                                                                    class_name="text-gray-600 mb-6",
                                                                ),
                                                                _preview_table_component(),
                                                                rx.el.details(
                                                                    rx.el.summary(
                                                                        "View Final Excel Columns Structure",
                                                                        class_name="cursor-pointer font-medium text-blue-600 hover:text-blue-800 mb-2 outline-none focus:ring-2 focus:ring-blue-300 rounded px-1",
                                                                    ),
                                                                    rx.el.ol(
                                                                        rx.foreach(
                                                                            FilePrepState.display_excel_columns,
                                                                            lambda col, index: rx.el.li(
                                                                                f"{index + 1}. {col['name']}",
                                                                                class_name="text-sm p-1",
                                                                            ),
                                                                        ),
                                                                        class_name="list-decimal list-inside p-3 border border-gray-200 rounded bg-gray-50 max-h-60 overflow-y-auto mt-2",
                                                                    ),
                                                                    class_name="mb-4",
                                                                ),
                                                                rx.el.details(
                                                                    rx.el.summary(
                                                                        "View Final Metrics & Weights",
                                                                        class_name="cursor-pointer font-medium text-blue-600 hover:text-blue-800 mb-2 outline-none focus:ring-2 focus:ring-blue-300 rounded px-1",
                                                                    ),
                                                                    rx.el.ul(
                                                                        rx.foreach(
                                                                            FilePrepState.all_included_metrics,
                                                                            lambda metric: rx.el.li(
                                                                                f"{metric['name']}: Weight {FilePrepState.metric_weights.get(metric['name'], 'N/A')}",
                                                                                class_name="text-sm p-1",
                                                                            ),
                                                                        ),
                                                                        class_name="list-disc list-inside p-3 border border-gray-200 rounded bg-gray-50 max-h-60 overflow-y-auto mt-2",
                                                                    ),
                                                                    rx.el.div(
                                                                        rx.el.strong(
                                                                            "Total Weight Sum: "
                                                                        ),
                                                                        FilePrepState.total_metric_weight,
                                                                        class_name="mt-2 font-semibold text-sm",
                                                                    ),
                                                                    class_name="mb-4",
                                                                ),
                                                                rx.el.details(
                                                                    rx.el.summary(
                                                                        "View Final Pass Criteria",
                                                                        class_name="cursor-pointer font-medium text-blue-600 hover:text-blue-800 mb-2 outline-none focus:ring-2 focus:ring-blue-300 rounded px-1",
                                                                    ),
                                                                    rx.el.div(
                                                                        rx.el.strong(
                                                                            "Threshold: "
                                                                        ),
                                                                        rx.cond(
                                                                            FilePrepState.pass_threshold
                                                                            != None,
                                                                            FilePrepState.pass_threshold.to_string(),
                                                                            rx.el.em(
                                                                                "Not Set",
                                                                                class_name="text-gray-500",
                                                                            ),
                                                                        ),
                                                                        class_name="text-sm mb-1",
                                                                    ),
                                                                    rx.el.div(
                                                                        rx.el.strong(
                                                                            "Definition:"
                                                                        ),
                                                                        rx.el.p(
                                                                            rx.cond(
                                                                                FilePrepState.pass_definition.length()
                                                                                > 0,
                                                                                FilePrepState.pass_definition,
                                                                                rx.el.em(
                                                                                    "Not Set",
                                                                                    class_name="text-gray-500",
                                                                                ),
                                                                            ),
                                                                            class_name="text-sm whitespace-pre-wrap mt-1",
                                                                        ),
                                                                    ),
                                                                    class_name="p-3 border border-gray-200 rounded bg-gray-50 max-h-60 overflow-y-auto mt-2 mb-4",
                                                                ),
                                                                rx.el.details(
                                                                    rx.el.summary(
                                                                        "View Final Read Me Content",
                                                                        class_name="cursor-pointer font-medium text-blue-600 hover:text-blue-800 mb-2 outline-none focus:ring-2 focus:ring-blue-300 rounded px-1",
                                                                    ),
                                                                    rx.el.div(
                                                                        rx.html(
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
                                                                rx.el.button(
                                                                    "Generate Evaluation Template (Not Implemented Yet)",
                                                                    class_name="w-full mt-4 px-6 py-3 bg-green-600 text-white rounded-lg shadow font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed",
                                                                ),
                                                                rx.el.div(
                                                                    rx.el.button(
                                                                        "⬅ Edit File Uploads",
                                                                        on_click=lambda: FilePrepState.set_template_preview_ready(
                                                                            False
                                                                        ),
                                                                        class_name="mr-4 mb-2 px-4 py-2 text-sm bg-yellow-500 text-white rounded hover:bg-yellow-600 transition duration-150",
                                                                    ),
                                                                    rx.el.button(
                                                                        "Edit Excel Columns",
                                                                        on_click=lambda: FilePrepState.set_column_structure_finalized(
                                                                            False
                                                                        ),
                                                                        class_name="mr-4 mb-2 px-4 py-2 text-sm bg-yellow-500 text-white rounded hover:bg-yellow-600 transition duration-150",
                                                                    ),
                                                                    rx.el.button(
                                                                        "Edit Metrics & Weighting",
                                                                        on_click=lambda: FilePrepState.set_metrics_confirmed(
                                                                            False
                                                                        ),
                                                                        class_name="mr-4 mb-2 px-4 py-2 text-sm bg-yellow-500 text-white rounded hover:bg-yellow-600 transition duration-150",
                                                                    ),
                                                                    rx.el.button(
                                                                        "Edit Stakeholder Perspective",
                                                                        on_click=lambda: FilePrepState.set_stakeholder_confirmed(
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
                                                                        "Edit MT Engines",
                                                                        on_click=lambda: FilePrepState.set_engines_confirmed(
                                                                            False
                                                                        ),
                                                                        class_name="mr-4 mb-2 px-4 py-2 text-sm bg-yellow-500 text-white rounded hover:bg-yellow-600 transition duration-150",
                                                                    ),
                                                                    rx.el.button(
                                                                        "Edit Language Pairs",
                                                                        on_click=lambda: FilePrepState.set_pairs_confirmed(
                                                                            False
                                                                        ),
                                                                        class_name="mr-4 mb-2 px-4 py-2 text-sm bg-yellow-500 text-white rounded hover:bg-yellow-600 transition duration-150",
                                                                    ),
                                                                    class_name="flex flex-wrap border-t border-gray-200 pt-4 mt-6",
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