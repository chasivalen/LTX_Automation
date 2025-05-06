import reflex as rx
from typing import TYPE_CHECKING, TypedDict
import logging
from app.states.file_prep_state import (
    DEFAULT_README_TEXT,
    EVERGREEN_METRICS,
    CustomMetric,
    ExcelColumn,
    DEFAULT_EXCEL_COLUMNS_DATA,
    FilePrepState,
)
from app.states.app_state import AppState

if TYPE_CHECKING:
    pass
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricsConfig(TypedDict):
    evergreen: list[str]
    custom: list[CustomMetric]


def get_default_excel_columns() -> list[ExcelColumn]:
    return [
        col.copy() for col in DEFAULT_EXCEL_COLUMNS_DATA
    ]


class ProjectState(rx.State):
    """Manages project creation, selection, and associated data for the LTX Bench flow."""

    projects: list[str] = []
    selected_project: str | None = None
    new_project_name: str = ""
    project_choice_in_dropdown: str | None = None
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
    project_excel_columns: dict[str, list[ExcelColumn]] = {
        "Default Project": get_default_excel_columns()
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
        if project_name not in self.project_excel_columns:
            self.project_excel_columns[project_name] = (
                get_default_excel_columns()
            )

    @rx.event
    async def create_project(self):
        """Creates a new project, selects it, initializes data, and notifies AppState."""
        project_name = self.new_project_name.strip()
        logger.info(
            f"Attempting to create project: {project_name}"
        )
        if (
            project_name
            and project_name not in self.projects
        ):
            temp_projects = self.projects.copy()
            temp_projects.append(project_name)
            self.projects = temp_projects
            self.selected_project = project_name
            self._initialize_project_data(project_name)
            self.new_project_name = ""
            self.project_choice_in_dropdown = project_name
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
                f"Project '{project_name}' created and loaded.",
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
    def set_project_choice_in_dropdown(
        self, project_name: str
    ):
        """Sets the project choice from the dropdown."""
        if project_name == "":
            self.project_choice_in_dropdown = None
        else:
            self.project_choice_in_dropdown = project_name

    @rx.event
    async def confirm_project_selection(self):
        """Confirms the selected project, loads its data, and updates AppState."""
        if (
            self.project_choice_in_dropdown
            and self.project_choice_in_dropdown
            in self.projects
        ):
            self.selected_project = (
                self.project_choice_in_dropdown
            )
            logger.info(
                f"Project '{self.selected_project}' confirmed and selected in state."
            )
            self._initialize_project_data(
                self.selected_project
            )
            yield AppState.set_project_selected(True)
            logger.info(
                "Yielded AppState.set_project_selected(True) for project confirmation."
            )
            yield FilePrepState.reset_state
            logger.info(
                "Yielded FilePrepState.reset_state for project confirmation."
            )
            yield rx.toast(
                f"Project '{self.selected_project}' settings loaded.",
                duration=3000,
            )
        elif self.project_choice_in_dropdown:
            logger.warning(
                f"Project confirmation failed: Project '{self.project_choice_in_dropdown}' not found in known projects."
            )
            yield rx.toast(
                f"Error: Project '{self.project_choice_in_dropdown}' not found.",
                duration=4000,
            )
            self.project_choice_in_dropdown = None
        else:
            logger.warning(
                "Project confirmation failed: No project choice made."
            )
            yield rx.toast(
                "Please select a project from the dropdown first.",
                duration=3000,
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
            list(
                self.project_language_pairs.get(
                    self.selected_project, []
                )
            )
            if self.selected_project
            else []
        )

    @rx.var
    def current_project_engines(self) -> list[str]:
        return (
            list(
                self.project_mt_engines.get(
                    self.selected_project, []
                )
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
        config = (
            self.project_included_metrics.get(
                self.selected_project
            )
            if self.selected_project
            else None
        )
        return config.copy() if config else None

    @rx.var
    def current_project_metric_weights(
        self,
    ) -> dict[str, int] | None:
        weights = (
            self.project_metric_weights.get(
                self.selected_project
            )
            if self.selected_project
            else None
        )
        return weights.copy() if weights else None

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

    @rx.var
    def current_project_excel_columns(
        self,
    ) -> list[ExcelColumn]:
        """Gets the base excel columns for the current project."""
        default_cols = get_default_excel_columns()
        cols_from_project = (
            self.project_excel_columns.get(
                self.selected_project, default_cols
            )
            if self.selected_project
            else default_cols
        )
        return [c.copy() for c in cols_from_project]