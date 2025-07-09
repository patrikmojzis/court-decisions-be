from pydantic import BaseModel, constr, Field

from app.utils.pydantic_utils import default_model_config


class SendGlobalNotificationSchema(BaseModel):
    title: constr(min_length=1, max_length=50) = Field(..., title="Aim for 15–30 characters to avoid truncation.")
    body: constr(min_length=1, max_length=178) = Field(..., title="About 4 lines of text.")

    model_config = default_model_config