from typing import Optional

from pydantic import BaseModel, constr

from app.utils.pydantic_utils import default_model_config


class UserPatchSchema(BaseModel):
    push_token: Optional[constr(max_length=255)] = None

    model_config = default_model_config