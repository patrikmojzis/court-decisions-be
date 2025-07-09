from pydantic import BaseModel

from app.utils.pydantic_utils import default_model_config


class SignInWithGoogleSchema(BaseModel):
    access_token: str

    model_config = default_model_config