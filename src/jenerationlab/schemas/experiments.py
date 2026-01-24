from typing import Any, Dict, Optional

from pydantic import BaseModel

from jenerationlab.schemas.registry import register

@register("experiments")
class ExperimentSchema(BaseModel):
    experiment_id: str = ""
    experiment_name: str = ""
    experiment_description: str = ""
    output_path: str = ""
    timestamp: str = ""

    generation_time: float | None = None
    batch_generation_time: float | None = None
   