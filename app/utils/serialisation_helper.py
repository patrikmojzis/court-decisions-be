from datetime import datetime

from bson import ObjectId


def serialise(val):
    if isinstance(val, ObjectId):
        return str(val)
    if isinstance(val, datetime):
        return val.isoformat()
    # insert serialisation here <start>

    # insert serialisation here <end>
    elif isinstance(val, list):
        return [serialise(item) for item in val]
    elif isinstance(val, dict):
        return {key: serialise(value) for key, value in val.items()}

    return val