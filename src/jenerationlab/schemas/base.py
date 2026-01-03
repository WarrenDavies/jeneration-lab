from typing import Any, Dict, Optional

from pydantic import BaseModel


class BaseSchema(BaseModel):
    experiment_id: str = ""
    experiment_name: str = ""
    experiment_description: str = ""
    filename: str = ""
    output_path: str = ""
    timestamp: str = ""
    model: str = ""
    device: str = ""
    generation_time: float | None = None
    batch_generation_time: float | None = None

    params: str = ""
    extras: str = ""