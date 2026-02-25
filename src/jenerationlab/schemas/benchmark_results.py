import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from jenerationlab.schemas.registry import register

@register("benchmark_results")
class BenchMarkResultsSchema(BaseModel):
    benchmark_run_id: str = ""
    experiment_id: str = ""
    score: float = None
    maximum: float = None
    percent: float = None
    ts: str = ""