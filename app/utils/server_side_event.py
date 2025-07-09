import json
from dataclasses import dataclass

from app.utils.serialisation_helper import serialise


@dataclass
class ServerSideEvent:
    event_type: str
    data: dict = None
    id: str = None
    retry: int = None

    def dump(self):
        message = []
        # if self.id is not None:
        #     message.append(f"id: {self.id}")
        if self.event_type is not None:
            message.append(f"event: {self.event_type}")
        # if self.retry is not None:
        #     message.append(f"retry: {self.retry}")
        if self.data is not None:
            message.append(f"data: {json.dumps(serialise(self.data))}")
        return "\n".join(message) + "\n\n"

    @classmethod
    def from_dict(cls, data):
        return cls(**data)