from flask import g, jsonify

from app.http_files.decorators.common_decorators import handle_exceptions
from app.http_files.resources.user_resource import UserResource
from app.http_files.schemas.sign_in_with_apple_schema import SignInWithAppleSchema
from app.http_files.services.sign_in_with_apple_service import sign_in
from app.models.auth_model import Auth
from app.utils.api_utils import validate_request


@handle_exceptions
def store():
    validate_request(SignInWithAppleSchema)
    identity_token = g.validated['identity_token']
    user = sign_in(identity_token)
    auth = Auth.create({'user_id': user.id, 'identification': 'apple'})

    return jsonify({'auth': auth.token, 'user': UserResource(user).dump()})

@handle_exceptions
def destroy():
    pass

@handle_exceptions
def revoke():
    pass


