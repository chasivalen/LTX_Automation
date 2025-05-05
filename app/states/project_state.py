import reflex as rx
from typing import Optional
from app.states.app_state import AppState


class ProjectState(rx.State):
    """Manages project creation and selection."""

    projects: list[str] = ["Default Project"]
    selected_project: str | None = None
    new_project_name: str = ""

    @rx.event
    def create_project(self):
        """Creates a new project if the name is not empty and not already taken."""
        if (
            self.new_project_name
            and self.new_project_name not in self.projects
        ):
            self.projects.append(self.new_project_name)
            self.selected_project = self.new_project_name
            self.new_project_name = ""
            yield AppState.set_project_selected(True)
        else:
            yield rx.toast(
                f"Project name '{self.new_project_name}' is invalid or already exists.",
                duration=4000,
            )

    @rx.event
    def select_project(self, project_name: str):
        """Selects an existing project."""
        if project_name:
            self.selected_project = project_name
            yield AppState.set_project_selected(True)

    @rx.var
    def has_selected_project(self) -> bool:
        """Checks if a project is currently selected."""
        return self.selected_project is not None