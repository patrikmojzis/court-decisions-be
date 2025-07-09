from flask import jsonify

from app.models.model_base import ModelBase
from app.utils.serialisation_helper import serialise


class ResourceBase:

    def __init__(self, data: ModelBase | list[ModelBase]):
        self._data = data

    def dump(self):
        return serialise(self.to_dict(self._data) if isinstance(self._data, ModelBase) else [self.to_dict(res) for res
                                                                                   in self._data])

    def to_response(self):
        return jsonify(self.dump())

    def to_dict(self, data: ModelBase) -> dict:
        return data.dict()
