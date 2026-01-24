import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class MeasurementSchema(BaseModel):
    measurement_id: str = ""
    artifact_id: str = ""
    experiment_id: str = ""
    timestamp: str = ""
    producer: str = ""
    measurement_name: str = ""
    value_int: Optional[int]
    value_float: Optional[float]
    value_str: Optional[str]
    value_bool: Optional[bool]
