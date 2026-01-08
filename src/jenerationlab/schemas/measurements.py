import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class MeasurementSchema(BaseModel):
    measurement_id: str = ""
    artifact_id: str = ""
    experiment_id: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)
    auto_metrics: Dict[str, Any] = {}
    ratings: Dict[str, Any] = {}


    rater_id: Optional[str] = "human_01"
    # generation_time: float | None = None
    # batch_generation_time: float | None = None


