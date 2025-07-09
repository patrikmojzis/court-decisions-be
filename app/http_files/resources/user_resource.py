from typing import TYPE_CHECKING

from app.http_files.resources.resource_base import ResourceBase

if TYPE_CHECKING:
    from app.models.user_model import User

class UserResource(ResourceBase):

    def to_dict(self, user: 'User'):
        return {
            '_id': user.id,
            'email': user.email,
        }