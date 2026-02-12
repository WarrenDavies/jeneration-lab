import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from jenerationlab.schemas.registry import register

@register("checks")
class ChecksSchema(BaseModel):
    check_id: str = ""
    case_id: str = ""
    artifact_id: str = ""
    experiment_id: str = ""
    timestamp: str = ""
    check_func: str = ""
    check_func_params: str = ""
    expected: str = ""
    actual: str = ""
