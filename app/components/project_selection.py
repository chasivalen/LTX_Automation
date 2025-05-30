import reflex as rx
from app.states.project_state import ProjectState


def project_selection_component() -> rx.Component:
    """Component for creating or selecting a project for LTX Bench."""
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "LTX Bench",
                class_name="text-3xl font-bold text-gray-900 text-center",
            ),
            rx.el.p(
                "Create or Select Project",
                class_name="text-lg text-gray-600 text-center mt-1 mb-6",
            ),
            class_name="mb-6",
        ),
        rx.el.div(
            rx.el.label(
                "Create New Project:",
                class_name="block text-sm font-medium text-gray-700 mb-1",
            ),
            rx.el.input(
                placeholder="Enter new project name",
                default_value=ProjectState.new_project_name,
                on_change=ProjectState.set_new_project_name,
                class_name="w-full p-2 border border-gray-300 rounded mb-2 focus:outline-none focus:ring-2 focus:ring-blue-500",
            ),
            rx.el.button(
                "Create Project",
                on_click=ProjectState.create_project,
                disabled=ProjectState.new_project_name.length()
                == 0,
                class_name="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed",
            ),
            class_name="mb-6",
        ),
        rx.el.div(
            rx.el.label(
                "Select Existing Project:",
                class_name="block text-sm font-medium text-gray-700 mb-1",
            ),
            rx.el.select(
                rx.el.option(
                    "Select a project...",
                    value="",
                    disabled=True,
                ),
                rx.foreach(
                    ProjectState.projects,
                    lambda project: rx.el.option(
                        project, value=project
                    ),
                ),
                on_change=ProjectState.set_project_choice_in_dropdown,
                value=rx.cond(
                    ProjectState.project_choice_in_dropdown,
                    ProjectState.project_choice_in_dropdown,
                    "",
                ),
                class_name="w-full p-2 border border-gray-300 rounded bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2",
            ),
            rx.el.button(
                "Load Project Settings",
                on_click=ProjectState.confirm_project_selection,
                disabled=(
                    ProjectState.project_choice_in_dropdown
                    == None
                )
                | (
                    ProjectState.project_choice_in_dropdown
                    == ""
                ),
                class_name="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed",
            ),
            class_name="mb-4",
        ),
        class_name="p-8 max-w-md mx-auto bg-white rounded-lg shadow-md border border-gray-200",
    )