import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from jenerationlab.schemas.registry import register

@register("case_results")
class CaseResultsSchema(BaseModel):
    case_result_id: str = ""
    experiment_id: str = ""
    benchmark_run_id: str = ""
    case_id: str = ""
    sum_of_check_scores: float = None
    required_check_score: float = None
    passed: int = None
    ts: str = ""
