from flask import g

from app.http_files.decorators.auth_decorators import protected_route
from app.http_files.decorators.common_decorators import handle_exceptions
from app.http_files.resources.user_resource import UserResource
from app.http_files.schemas.user_patch_schema import UserPatchSchema
from app.utils.api_utils import validate_request


@handle_exceptions
@protected_route
def current():
    return UserResource(g.get("user")).to_response()


@handle_exceptions
@protected_route
def destroy():
    user = g.get("user")
    user.delete()
    return {"message": "User deleted"}


@handle_exceptions
@protected_route
def update():
    validate_request(UserPatchSchema, exclude_unset=True)
    user = g.get("user")
    user.update(g.validated)
    return UserResource(user).to_response()