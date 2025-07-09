from pydantic import BaseModel

from app.utils.pydantic_utils import default_model_config


class SignInWithPasswordSchema(BaseModel):
    email: str
    password: str

    model_config = default_model_config