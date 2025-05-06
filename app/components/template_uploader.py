import reflex as rx
from app.states.file_prep_state import (
    FilePrepState,
    ExcelColumn,
    MAX_PREVIEW_ROWS,
)
from typing import List, Dict


def _file_uploader_for_column(
    col_item: ExcelColumn,
) -> rx.Component:
    """Creates a file upload interface for a specific input column."""
    column_id = col_item["id"]
    column_name = col_item["name"]
    upload_id = f"upload_{column_id}"
    file_info_str = FilePrepState.uploaded_file_info.get(
        column_id, ""
    )
    is_file_uploaded = file_info_str != ""
    return rx.el.div(
        rx.el.h6(
            f"Upload for '{column_name}'",
            class_name="text-md font-medium mb-2 text-gray-700",
        ),
        rx.cond(
            is_file_uploaded,
            rx.el.div(
                rx.el.p(
                    rx.el.span(
                        "Uploaded: ",
                        class_name="font-semibold",
                    ),
                    file_info_str,
                    class_name="text-sm text-green-700 bg-green-100 p-2 rounded mb-2",
                ),
                rx.el.button(
                    "Clear Upload",
                    on_click=lambda: FilePrepState.clear_uploaded_file(
                        column_id
                    ),
                    class_name="px-3 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600",
                ),
                class_name="mb-2",
            ),
            rx.upload.root(
                rx.el.div(
                    rx.icon(
                        tag="cloud_upload",
                        class_name="w-8 h-8 mb-2 text-gray-500",
                    ),
                    rx.el.p(
                        rx.el.span(
                            f"Click to upload for {column_name}",
                            class_name="font-semibold",
                        ),
                        " or drag and drop",
                        class_name="text-xs text-gray-600",
                    ),
                    rx.el.span(
                        ".txt, .csv, .tsv",
                        class_name="text-xs text-gray-500",
                    ),
                    class_name="flex flex-col items-center justify-center py-4 px-2 text-center",
                ),
                id=upload_id,
                multiple=False,
                accept={
                    "text/plain": [".txt"],
                    "text/csv": [".csv"],
                    "text/tab-separated-values": [".tsv"],
                },
                on_drop=FilePrepState.handle_file_upload(
                    rx.upload_files(upload_id=upload_id),
                    column_id,
                ),
                border="2px dashed #d1d5db",
                padding="1rem",
                class_name="bg-gray-50 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors",
            ),
        ),
        class_name="mb-6 p-4 border border-gray-200 rounded-lg bg-white shadow-sm",
    )


def template_uploader_component() -> rx.Component:
    """Component for uploading files for input columns and previewing data."""
    return rx.el.div(
        rx.el.h4(
            "Step 7: Pre-load Template with Input Data",
            class_name="text-xl font-medium mb-6 text-gray-700",
        ),
        rx.el.p(
            "Upload files for the 'File Name', 'Source', and 'Target' input columns. These will populate the initial rows of your evaluation template.",
            class_name="text-sm text-gray-600 mb-4",
        ),
        rx.foreach(
            FilePrepState.template_input_columns_for_upload,
            _file_uploader_for_column,
        ),
        rx.el.div(
            rx.el.button(
                "⬅ Edit Excel Columns",
                on_click=lambda: FilePrepState.set_column_structure_finalized(
                    False
                ),
                class_name="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 transition duration-150",
            ),
            rx.el.button(
                "Generate Template Preview ➡",
                on_click=FilePrepState.proceed_to_generate_template_preview,
                class_name="px-6 py-3 bg-blue-600 text-white rounded-lg shadow font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition duration-150",
            ),
            class_name="flex justify-between items-center mt-6 border-t border-gray-200 pt-4",
        ),
        class_name="p-4 border border-gray-200 rounded-lg bg-gray-50 shadow",
    )