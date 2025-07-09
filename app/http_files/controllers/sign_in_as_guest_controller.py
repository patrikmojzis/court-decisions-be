from flask import jsonify

from app.http_files.decorators.common_decorators import handle_exceptions
from app.http_files.resources.user_resource import UserResource
from app.models.auth_model import Auth
from app.models.user_model import User


@handle_exceptions
def store():
    user = User.create({"is_guest": True})
    auth = Auth.create({'user_id': user.id, 'identification': 'guest'})
    return jsonify({'auth': auth.token, 'user': UserResource(user).dump()})
