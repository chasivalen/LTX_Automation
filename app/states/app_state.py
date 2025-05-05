import reflex as rx
from typing import Literal

ViewType = Literal[
    "default",
    "file_prep",
    "final_file_prep",
    "update_tableau",
    "seo_automation",
]
ProjectType = Literal["MT", "LLM", "Gen AI"]


class AppState(rx.State):
    """Manages the overall application state."""

    project_selected: bool = False
    selected_view: ViewType = "default"
    file_prep_project_type: ProjectType | None = None

    @rx.event
    def set_selected_view(self, view: ViewType):
        """Sets the currently active view based on sidebar selection."""
        self.selected_view = view
        if view != "file_prep":
            self.file_prep_project_type = None

    @rx.event
    def set_file_prep_project_type(
        self, project_type: ProjectType
    ):
        """Sets the project type for the File Prep view."""
        self.file_prep_project_type = project_type