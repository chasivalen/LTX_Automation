import reflex as rx
from typing import Literal, Optional

ViewType = Literal[
    "default",
    "file_prep",
    "final_file_prep",
    "update_tableau",
    "seo_automation",
]
ProjectType = Literal["MT", "LLM", "Gen AI"]
InitialChoiceType = Literal["SEO", "LTX Bench"]


class AppState(rx.State):
    """Manages the overall application state."""

    initial_choice: InitialChoiceType | None = None
    project_selected: bool = False
    selected_view: ViewType = "default"
    file_prep_project_type: ProjectType | None = None

    @rx.event
    def set_initial_choice(self, choice: InitialChoiceType):
        """Sets the initial choice between SEO and LTX Bench."""
        self.initial_choice = choice
        self.project_selected = False
        self.selected_view = "default"
        self.file_prep_project_type = None

    @rx.event
    def reset_initial_choice(self):
        """Resets the initial choice and related states."""
        self.initial_choice = None
        self.project_selected = False
        self.selected_view = "default"
        self.file_prep_project_type = None

    @rx.event
    def set_project_selected(self, selected: bool):
        """Sets the project selected state for the LTX Bench flow."""
        self.project_selected = selected
        if not selected:
            self.selected_view = "default"
            self.file_prep_project_type = None

    @rx.event
    def set_selected_view(self, view: ViewType):
        """Sets the currently active view within the LTX Bench flow."""
        self.selected_view = view
        if view != "file_prep":
            self.file_prep_project_type = None

    @rx.event
    def set_file_prep_project_type(
        self, project_type: ProjectType
    ):
        """Sets the project type for the File Prep view (within LTX Bench)."""
        self.file_prep_project_type = project_type