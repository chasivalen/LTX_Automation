import reflex as rx
from typing import Optional, TypedDict
import logging
from app.states.file_prep_state import (
    DEFAULT_README_TEXT,
    EVERGREEN_METRICS,
    CustomMetric,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricsConfig(TypedDict):
    evergreen: list[str]
    custom: list[CustomMetric]


class ProjectState(rx.State):
    """Manages project creation, selection, and associated data for the LTX Bench flow."""

    projects: list[str] = ["Default Project"]
    selected_project: str | None = None
    new_project_name: str = ""
    project_language_pairs: dict[
        str, list[tuple[str, str]]
    ] = {"Default Project": []}
    project_mt_engines: dict[str, list[str]] = {
        "Default Project": []
    }
    project_readme_content: dict[str, str] = {
        "Default Project": DEFAULT_README_TEXT
    }
    project_stakeholder_comments: dict[str, str] = {
        "Default Project": ""
    }
    project_included_metrics: dict[str, MetricsConfig] = {
        "Default Project": {
            "evergreen": list(EVERGREEN_METRICS.keys()),
            "custom": [],
        }
    }
    project_metric_weights: dict[str, dict[str, int]] = {
        "Default Project": {
            metric: 5 for metric in EVERGREEN_METRICS
        }
    }
    project_pass_threshold: dict[str, float | None] = {
        "Default Project": None
    }
    project_pass_definition: dict[str, str] = {
        "Default Project": ""
    }

    def _initialize_project_data(self, project_name: str):
        """Initializes all data structures for a newly created project."""
        if project_name not in self.project_language_pairs:
            self.project_language_pairs[project_name] = []
        if project_name not in self.project_mt_engines:
            self.project_mt_engines[project_name] = []
        if project_name not in self.project_readme_content:
            self.project_readme_content[project_name] = (
                DEFAULT_README_TEXT
            )
        if (
            project_name
            not in self.project_stakeholder_comments
        ):
            self.project_stakeholder_comments[
                project_name
            ] = ""
        if (
            project_name
            not in self.project_included_metrics
        ):
            self.project_included_metrics[project_name] = {
                "evergreen": list(EVERGREEN_METRICS.keys()),
                "custom": [],
            }
        if project_name not in self.project_metric_weights:
            self.project_metric_weights[project_name] = {
                metric: 5 for metric in EVERGREEN_METRICS
            }
        if project_name not in self.project_pass_threshold:
            self.project_pass_threshold[project_name] = None
        if project_name not in self.project_pass_definition:
            self.project_pass_definition[project_name] = ""

    @rx.event
    async def create_project(self):
        """Creates a new project, selects it, initializes data, and notifies AppState."""
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
            self._initialize_project_data(project_name)
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
        """Selects an existing project, ensures data exists, notifies AppState, and resets FilePrepState."""
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
            self._initialize_project_data(project_name)
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
        """Sets the name for a potential new project."""
        self.new_project_name = name

    @rx.var
    def has_selected_project(self) -> bool:
        """Checks if a project is currently selected."""
        return self.selected_project is not None

    @rx.var
    def current_project_pairs(
        self,
    ) -> list[tuple[str, str]]:
        return (
            self.project_language_pairs.get(
                self.selected_project, []
            )
            if self.selected_project
            else []
        )

    @rx.var
    def current_project_engines(self) -> list[str]:
        return (
            self.project_mt_engines.get(
                self.selected_project, []
            )
            if self.selected_project
            else []
        )

    @rx.var
    def current_project_readme(self) -> str:
        return (
            self.project_readme_content.get(
                self.selected_project, DEFAULT_README_TEXT
            )
            if self.selected_project
            else DEFAULT_README_TEXT
        )

    @rx.var
    def current_project_stakeholder_comments(self) -> str:
        return (
            self.project_stakeholder_comments.get(
                self.selected_project, ""
            )
            if self.selected_project
            else ""
        )

    @rx.var
    def current_project_metrics_config(
        self,
    ) -> MetricsConfig | None:
        return (
            self.project_included_metrics.get(
                self.selected_project, None
            )
            if self.selected_project
            else None
        )

    @rx.var
    def current_project_metric_weights(
        self,
    ) -> dict[str, int] | None:
        return (
            self.project_metric_weights.get(
                self.selected_project, None
            )
            if self.selected_project
            else None
        )

    @rx.var
    def current_project_pass_threshold(
        self,
    ) -> float | None:
        return (
            self.project_pass_threshold.get(
                self.selected_project, None
            )
            if self.selected_project
            else None
        )

    @rx.var
    def current_project_pass_definition(self) -> str:
        return (
            self.project_pass_definition.get(
                self.selected_project, ""
            )
            if self.selected_project
            else ""
        )