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

    async def _reset_file_prep_state(self):
        """Helper to reset the file prep state."""
        from app.states.file_prep_state import FilePrepState

        file_prep_state = await self.get_state(
            FilePrepState
        )
        yield file_prep_state.reset_state()

    @rx.event
    async def set_initial_choice(
        self, choice: InitialChoiceType
    ):
        """Sets the initial choice between SEO and LTX Bench."""
        async with self:
            self.initial_choice = choice
            self.project_selected = False
            self.selected_view = "default"
            self.file_prep_project_type = None
        yield self._reset_file_prep_state()

    @rx.event
    async def reset_initial_choice(self):
        """Resets the initial choice and related states."""
        async with self:
            self.initial_choice = None
            self.project_selected = False
            self.selected_view = "default"
            self.file_prep_project_type = None
        yield self._reset_file_prep_state()

    @rx.event
    async def set_project_selected(self, selected: bool):
        """Sets the project selected state for the LTX Bench flow."""
        async with self:
            self.project_selected = selected
            if not selected:
                self.selected_view = "default"
                self.file_prep_project_type = None
        if not selected:
            yield self._reset_file_prep_state()

    @rx.event
    async def set_selected_view(self, view: ViewType):
        """Sets the currently active view within the LTX Bench flow."""
        old_view = self.selected_view
        async with self:
            self.selected_view = view
            if (
                old_view == "file_prep"
                and view != "file_prep"
            ):
                self.file_prep_project_type = None
        if old_view == "file_prep" and view != "file_prep":
            yield self._reset_file_prep_state()
        elif (
            view == "file_prep" and old_view != "file_prep"
        ):
            yield self._reset_file_prep_state()
        elif (
            view == "file_prep" and old_view == "file_prep"
        ):
            pass

    @rx.event
    async def set_file_prep_project_type(
        self, project_type: ProjectType
    ):
        """Sets the project type for the File Prep view (within LTX Bench)."""
        async with self:
            self.file_prep_project_type = project_type
        yield self._reset_file_prep_state()