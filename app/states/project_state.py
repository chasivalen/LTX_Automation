import reflex as rx
from typing import Optional


class ProjectState(rx.State):
    """Manages project creation and selection for the LTX Bench flow."""

    projects: list[str] = ["Default Project"]
    selected_project: str | None = None
    new_project_name: str = ""
    project_language_pairs: dict[
        str, list[tuple[str, str]]
    ] = {"Default Project": []}

    @rx.event
    async def create_project(self):
        """Creates a new project if the name is not empty and not already taken."""
        from app.states.app_state import AppState
        from app.states.file_prep_state import FilePrepState

        if (
            self.new_project_name
            and self.new_project_name not in self.projects
        ):
            self.projects.append(self.new_project_name)
            self.selected_project = self.new_project_name
            self.project_language_pairs[
                self.new_project_name
            ] = []
            self.new_project_name = ""
            app_state = await self.get_state(AppState)
            yield app_state.set_project_selected(True)
            file_prep_state = await self.get_state(
                FilePrepState
            )
            yield file_prep_state.reset_state()
        else:
            yield rx.toast(
                f"Project name '{self.new_project_name}' is invalid or already exists.",
                duration=4000,
            )

    @rx.event
    async def select_project(self, project_name: str):
        """Selects an existing project for the LTX Bench flow."""
        from app.states.app_state import AppState
        from app.states.file_prep_state import FilePrepState

        if project_name:
            self.selected_project = project_name
            app_state = await self.get_state(AppState)
            yield app_state.set_project_selected(True)
            file_prep_state = await self.get_state(
                FilePrepState
            )
            yield file_prep_state.reset_state()

    @rx.var
    def has_selected_project(self) -> bool:
        """Checks if a project is currently selected within the LTX Bench flow."""
        return self.selected_project is not None

    @rx.var
    def current_project_pairs(
        self,
    ) -> list[tuple[str, str]]:
        """Gets the language pairs for the currently selected project."""
        if self.selected_project:
            return self.project_language_pairs.get(
                self.selected_project, []
            )
        return []