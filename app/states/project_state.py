import reflex as rx
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProjectState(rx.State):
    """Manages project creation, selection, and associated data (like language pairs and engines) for the LTX Bench flow."""

    projects: list[str] = ["Default Project"]
    selected_project: str | None = None
    new_project_name: str = ""
    project_language_pairs: dict[
        str, list[tuple[str, str]]
    ] = {"Default Project": []}
    project_mt_engines: dict[str, list[str]] = {
        "Default Project": []
    }

    @rx.event
    async def create_project(self):
        """
        Creates a new project, selects it, and notifies AppState.
        Resets FilePrepState for the new project context.
        Shows a toast message on failure (invalid name or duplicate).
        """
        from app.states.app_state import AppState
        from app.states.file_prep_state import FilePrepState

        project_name = self.new_project_name.strip()
        logger.info(
            f"Attempting to create project: {project_name}"
        )
        if (
            project_name
            and project_name not in self.projects
        ):
            self.projects.append(project_name)
            self.selected_project = project_name
            self.project_language_pairs[project_name] = []
            self.project_mt_engines[project_name] = []
            self.new_project_name = ""
            logger.info(
                f"Project '{project_name}' added to state."
            )
            yield AppState.set_project_selected(True)
            logger.info(
                "Yielded AppState.set_project_selected(True)"
            )
            yield FilePrepState.reset_state
            logger.info("Yielded FilePrepState.reset_state")
            yield rx.toast(
                f"Project '{project_name}' created.",
                duration=3000,
            )
            logger.info("Project creation toast yielded.")
        else:
            error_msg = (
                f"Project name '{project_name}' is invalid or already exists."
                if project_name
                else "Project name cannot be empty."
            )
            logger.warning(
                f"Project creation failed: {error_msg}"
            )
            yield rx.toast(error_msg, duration=4000)

    @rx.event
    async def select_project(self, project_name: str):
        """
        Selects an existing project, notifies AppState, and resets FilePrepState.
        """
        from app.states.app_state import AppState
        from app.states.file_prep_state import FilePrepState

        logger.info(
            f"Attempting to select project: {project_name}"
        )
        if project_name and project_name in self.projects:
            self.selected_project = project_name
            logger.info(
                f"Project '{project_name}' selected in state."
            )
            if (
                project_name
                not in self.project_language_pairs
            ):
                self.project_language_pairs[
                    project_name
                ] = []
            if project_name not in self.project_mt_engines:
                self.project_mt_engines[project_name] = []
            yield AppState.set_project_selected(True)
            logger.info(
                "Yielded AppState.set_project_selected(True) for project selection."
            )
            yield FilePrepState.reset_state
            logger.info(
                "Yielded FilePrepState.reset_state for project selection."
            )
        elif project_name:
            logger.warning(
                f"Project selection failed: Project '{project_name}' not found."
            )
            yield rx.toast(
                f"Error: Project '{project_name}' not found.",
                duration=4000,
            )
        else:
            logger.warning(
                "Project selection failed: No project name provided."
            )

    @rx.event
    def set_new_project_name(self, name: str):
        self.new_project_name = name

    @rx.var
    def has_selected_project(self) -> bool:
        """Checks if a project is currently selected."""
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

    @rx.var
    def current_project_engines(self) -> list[str]:
        """Gets the MT engines for the currently selected project."""
        if self.selected_project:
            return self.project_mt_engines.get(
                self.selected_project, []
            )
        return []