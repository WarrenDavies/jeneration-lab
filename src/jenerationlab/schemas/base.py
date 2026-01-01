from typing import Any, Dict, Optional

from pydantic import BaseModel


class BaseSchema(BaseModel):
    filename: str = ""
    output_path: str = ""
    timestamp: str = ""
    model: str = ""
    device: str = ""
    generation_time: float | None = None
    batch_generation_time: float | None = None

    params: Dict[str, Any] = {} 
    extras: Dict[str, Any] = {}

    # SD 1.5 params
    # dtype: str = ""
    # seed: int = 0
    # height: int = 0
    # width: int = 0
    # inf_steps: int = 0
    # guidance_scale: float = 0
    # enable_attention_slicing: bool = True
    # scheduler: str = ""
    