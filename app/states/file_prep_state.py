
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
    Any, # Added for rx.upload_files if return type is complex
)
import uuid
import re
import io
import csv
import logging
import html

if TYPE_CHECKING:
    from .project_state import ProjectState # Adjusted import for co-located states

logger = logging.getLogger(__name__)
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
    id: str
    name: str
    group: ColumnGroup
    editable_name: bool
    removable: bool
    movable_within_group: bool
    is_default: bool
    formula_description: Optional[str]
    formula_excel_style: Optional[str]
    metric_type: Optional[
        Literal["evergreen", "custom", "overall"]
    ]
    requires_upload: Optional[bool]
    is_word_count_column: Optional[bool]
    is_first_movable_in_group: Optional[bool] # Calculated, not stored in project
    is_last_movable_in_group: Optional[bool] # Calculated, not stored in project


DEFAULT_EXCEL_COLUMNS_DATA: List[ExcelColumn] = [
    {
        "id": str(uuid.uuid4()), "name": "File Name", "group": "Input", 
        "editable_name": False, "removable": False, "movable_within_group": False, 
        "is_default": True, "requires_upload": True
    },
    {
        "id": str(uuid.uuid4()), "name": "Source", "group": "Input",
        "editable_name": False, "removable": False, "movable_within_group": False,
        "is_default": True, "requires_upload": True
    },
    {
        "id": str(uuid.uuid4()), "name": "Target", "group": "Input",
        "editable_name": False, "removable": False, "movable_within_group": False,
        "is_default": True, "requires_upload": True
    },
    {
        "id": str(uuid.uuid4()), "name": "Word Count (Source)", "group": "Pre-Evaluation",
        "editable_name": False, "removable": False, "movable_within_group": False, "is_default": True,
        "is_word_count_column": True,
        "formula_description": "Calculates word count of the Source column.",
        "formula_excel_style": "" # Example: =IF(ISBLANK(B2),0,LEN(TRIM(B2))-LEN(SUBSTITUTE(TRIM(B2),\" \",\"\"))+1) (adapt B2)
    },
    {
        "id": str(uuid.uuid4()), "name": "Overall Score", "group": "Calculated Score",
        "editable_name": False, "removable": False, "movable_within_group": False, "is_default": True,
        "metric_type": "overall",
        "formula_description": "Weighted average of all scoring metrics. Formula is auto-generated based on selected metrics and weights.",
        "formula_excel_style": "" # Will be dynamically generated
    },
    {
        "id": str(uuid.uuid4()), "name": "General Comments", "group": "Freeform",
        "editable_name": True, "removable": True, "movable_within_group": True, "is_default": True
    },
]

DEFAULT_README_HTML = """<h2>Evaluation Instructions</h2>
