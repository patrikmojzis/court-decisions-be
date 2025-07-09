from flask import g, jsonify

from app.http_files.decorators.common_decorators import handle_exceptions
from app.http_files.resources.user_resource import UserResource
from app.http_files.schemas.sign_in_with_google_schema import SignInWithGoogleSchema
from app.http_files.services.sign_in_with_google_service import sign_in
from app.models.auth_model import Auth
from app.utils.api_utils import validate_request


@handle_exceptions
def store():
    validate_request(SignInWithGoogleSchema)
    access_token = g.validated['access_token']
    user = sign_in(access_token)
    auth = Auth.create({'user_id': user.id, 'identification': 'google'})

    return jsonify({'auth': auth.token, 'user': UserResource(user).dump()})

@handle_exceptions
def destroy():
    pass
