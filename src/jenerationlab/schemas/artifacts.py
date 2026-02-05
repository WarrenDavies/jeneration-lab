from typing import Any, Dict, Optional

from pydantic import BaseModel

from jenerationlab.schemas.registry import register

@register("artifacts")
class ArtifactSchema(BaseModel):
    artifact_id: str = ""
    experiment_id: str = ""
    filename: str = ""
    model: str = ""
    model_path: str = ""
    device: str = ""
    params: str = ""
    extras: str = ""
    timestamp: str = ""
    params: str = ""
    extras: str = ""
