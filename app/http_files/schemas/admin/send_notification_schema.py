from bson import ObjectId
from pydantic import BaseModel, constr, Field, field_validator
from pydantic_core.core_schema import ValidationInfo

from app.utils.pydantic_utils import default_model_config


class SendNotificationSchema(BaseModel):
    title: constr(min_length=1, max_length=50) = Field(..., title="Aim for 15–30 characters to avoid truncation.")
    body: constr(min_length=1, max_length=178) = Field(..., title="About 4 lines of text.")
    user_id: constr(min_length=1, max_length=255) = Field(..., title="User ID to send notification to.")

    model_config = default_model_config

    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v: str, info: ValidationInfo):
        if not ObjectId.is_valid(v):
            raise ValueError("user_id is not a valid ObjectId.")
        return v
