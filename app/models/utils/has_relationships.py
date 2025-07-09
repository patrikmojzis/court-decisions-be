from typing import TYPE_CHECKING, Optional

from bson import ObjectId

if TYPE_CHECKING:
    from app.models.model_base import T


class HasRelationships:

    def __init__(self, *args, **kwargs):
        pass

    def belongs_to(self, parent_model, parent_key=None, child_key=None) -> Optional['T']:
        parent_model = parent_model
        parent_key = parent_key or '_id'
        child_key = child_key or f'{parent_model.__name__.lower()}_id'
        if getattr(self, child_key, None) is None:
            return None

        return parent_model.find_one({parent_key: self._get_object_id(child_key)})

    def has_one(self, child_model, parent_key=None, child_key=None) -> Optional['T']:
        child_model = child_model
        parent_key = parent_key or '_id'
        child_key = child_key or f'{self.__class__.__name__.lower()}_id'
        if getattr(self, parent_key, None) is None:
            return None

        return child_model.find_one({child_key: self._get_object_id(parent_key)})

    def has_many(self, child_model, parent_key=None, child_key=None) -> list['T']:
        child_model = child_model
        parent_key = parent_key or '_id'
        child_key = child_key or f'{self.__class__.__name__.lower()}_id'
        if getattr(self, parent_key, None) is None:
            return []

        return child_model.find({child_key: self._get_object_id(parent_key)})

    def _get_object_id(self, key: str) -> ObjectId:
        val = getattr(self, key)
        if isinstance(val, ObjectId):
            return val
        else:
            return ObjectId(val)