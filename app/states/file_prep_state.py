
import reflex as rx
from typing import (
    Literal,
    TypedDict,
    TYPE_CHECKING,
    Optional,
    Union,
    List,
    Dict,
    cast,
    Any,
)
import uuid
import re
import io
import csv
import logging
import html
from app.states.project_state import ProjectState # Full import to avoid circular issues at runtime for type hints if needed

if TYPE_CHECKING:
    from app.states.project_state import ProjectState

logger = logging.getLogger(__name__)

# --- Constants ---
MAX_PREVIEW_ROWS = 10

Language = Literal[
    "Arabic",
    "English",
    "Spanish",
    "French",
    "German",
    "Korean",
    "Japanese",
    "Chinese",
]
AVAILABLE_LANGUAGES: List[Language] = [
    "English",
    "Spanish",
    "French",
    "German",
    "Korean",
    "Japanese",
    "Chinese",
    "Arabic",
]

DEFAULT_MT_ENGINES: List[str] = [
    "Google Translate",
    "DeepL",
    "Microsoft Translator",
    "Amazon Translate",
]

EVERGREEN_METRICS: Dict[str, str] = {
    "Fluency": "How natural and easy to read the translation is.",
    "Accuracy": "How well the translation conveys the meaning of the source text.",
    "Style": "Appropriateness of the translation's tone and register for the intended audience and purpose.",
    "Terminology": "Correct and consistent use of domain-specific terms.",
    "Locale Conventions": "Correct use of formatting for dates, numbers, currency, etc., appropriate for the target locale.",
}

# --- Type Definitions ---
ReadmeChoice = Literal["default", "customize", "new"]
ColumnGroup = Literal[
    "Input",
    "Pre-Evaluation",
    "Scoring",
    "Calculated Score",
    "Freeform",
]

COLUMN_GROUPS_ORDER: List[ColumnGroup] = [
    "Input",
    "Pre-Evaluation",
    "Scoring",
    "Calculated Score",
    "Freeform",
]


class CustomMetric(TypedDict):
    name: str
    definition: str


class ExcelColumn(TypedDict, total=False):
    id: str # Unique ID for the column
    name: str # Display name of the column
    group: ColumnGroup # Group the column belongs to
    editable_name: bool # Can the user rename this column? (default: True for custom, False for default)
    removable: bool # Can the user remove this column? (default: True for custom, False for key defaults)
    movable_within_group: bool # Can this column be moved within its group?
    is_default: bool # Is this a default column that might have special handling?
    # For formula-based or calculated columns
    formula_description: Optional[str] # Human-readable description of how it's calculated
    formula_excel_style: Optional[str] # Excel-style formula string (e.g., =A1+B1)
    # For scoring columns
    metric_type: Optional[Literal["evergreen", "custom", "overall"]]
    # For columns that expect file uploads to populate them
    requires_upload: Optional[bool]
    # For Word Count column specifically
    is_word_count_column: Optional[bool]
    # UI state, not necessarily for storage but for display logic
    is_first_movable_in_group: Optional[bool]
    is_last_movable_in_group: Optional[bool]


DEFAULT_README_HTML = """
