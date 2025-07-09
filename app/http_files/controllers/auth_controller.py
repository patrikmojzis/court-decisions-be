from flask import g, jsonify

from app.exceptions.http_exception import HttpException
from app.http_files.decorators.auth_decorators import protected_route
from app.http_files.decorators.common_decorators import handle_exceptions
from app.http_files.schemas.sign_in_with_password_schema import SignInWithPasswordSchema
from app.models.auth_model import Auth
from app.models.user_model import User
from app.utils.api_utils import validate_request
from app.utils.auth_utils import hash_password


@handle_exceptions
@protected_route
def destroy():
    g.get("auth").delete()
    return '', 204


@handle_exceptions
def sign_in_with_password():
    validate_request(SignInWithPasswordSchema)
    user = User.find_one({'email': g.validated['email']})
    if not user:
        raise HttpException('user_not_found', 404)
    if not hash_password(str(g.validated['password'])) == user.password:
        raise HttpException('invalid_password', 401)
    
    auth = Auth.create({'user_id': user.id})
    return jsonify({'token': auth.token})