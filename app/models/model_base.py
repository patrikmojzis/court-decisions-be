# app/models/model_base.py
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, TypeVar, ClassVar, Any, get_type_hints
from typing import TYPE_CHECKING

from bson import ObjectId
from pymongo import TEXT

from app.db.mongo import get_db
from app.exceptions.database_not_initialized import DatabaseNotInitialized
from app.exceptions.http_exception import HttpException
from app.models.utils.has_observers import HasObservers
from app.models.utils.has_relationships import HasRelationships

if TYPE_CHECKING:
    from pymongo.collection import Collection


T = TypeVar('T', bound='ModelBase')


@dataclass
class ModelBase(HasRelationships, HasObservers):
    protected: ClassVar[list[str]] = ["_id", "created_at", "updated_at"]
    searchable: ClassVar[Optional[list[str]]] = None

    _id: Optional[ObjectId] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        HasRelationships.__init__(self)
        HasObservers.__init__(self)

        self.clean: dict[str, Any] = {}

        for key in self.model_fields().keys():
            super().__setattr__(key, kwargs.get(key))

    @classmethod
    def collection_cls(cls) -> 'Collection':
        db = get_db()
        if db is None:
            raise DatabaseNotInitialized()
        return db[cls.__name__.lower()]

    def collection(self) -> 'Collection':
        db = get_db()
        if db is None:
            raise DatabaseNotInitialized()
        return db[self.__class__.__name__.lower()]

    def save(self: T) -> T:
        if self._id:
            self._update()
        else:
            self._create()
        self.refresh()
        return self

    @classmethod
    def model_fields(cls) -> dict[str, Any]:
        annotations = {}
        for base in cls.__mro__:
            if hasattr(base, '__annotations__'):
                annotations.update(get_type_hints(base))

        del annotations["protected"]
        del annotations["searchable"]

        return annotations

    @classmethod
    def fillable_fields(cls) -> list[str]:
        return [f for f in cls.model_fields().keys() if f not in cls.protected]

    @classmethod
    def all_fields(cls) -> list[str]:
        return [key for key in cls.model_fields().keys()]

    def _update(self):
        [observer.on_updating(self) for observer in self.observers]
        (self.collection()).update_one(
            self._query({'_id': self._id}),
            {
                '$set': {key: self.get(key) for key in self.fillable_fields() if self.is_dirty(key)},
                '$currentDate': {'updated_at': True}
            }
        )
        self.refresh()
        [observer.on_updated(self) for observer in self.observers]

    def _create(self):
        [observer.on_creating(self) for observer in self.observers]
        data = self._query({
            **{key: self.get(key) for key in self.fillable_fields()},
            'created_at': self.get('created_at') or datetime.now(),
            'updated_at': self.get('updated_at') or datetime.now(),
        })
        result = (self.collection()).insert_one(data)
        self._id = result.inserted_id
        self.refresh()
        [observer.on_created(self) for observer in self.observers]

    @classmethod
    def create(cls: type[T], data: dict[str, any]) -> T:
        instance = cls(**cls._query(data))
        instance.save()
        return instance

    @classmethod
    def all(cls: type[T]) -> list[T]:
        return [cls(**data) for data in (cls.collection_cls()).find(cls._query({}))]

    def refresh(self: T) -> T:
        data = (self.collection()).find_one({'_id': self._id})
        if data:
            for key, value in data.items():
                setattr(self, key, value)
            self.clean = {}
        return self

    @classmethod
    def search(cls: type[T], query: str | dict[str, any] | ObjectId, limit: Optional[int] = 10,
                     skip: Optional[int] = 0, sort: Optional[list[tuple[str, int]]] = None) -> dict[str, any]:
        if isinstance(query, int):
            query = str(query)

        if isinstance(query, ObjectId):
            mongo_query = {"$or": [{key: query} for key in cls.all_fields()]}
        elif isinstance(query, dict):
            mongo_query = query
        elif isinstance(query, str):
            mongo_query = cls.build_search_query_from_string(query)
        else:
            raise ValueError("[model_base, search] Query must be a string, dict, or ObjectId.")

        mongo_query = cls._query(mongo_query)
        data = cls.find(mongo_query, limit=limit, skip=skip, sort=sort)
        total = cls.count(mongo_query)
        return {
            "meta": {
                "total": total,
                "displaying": len(data),
                "limit": limit,
                "skip": skip
            },
            "data": data
        }

    @classmethod
    def build_search_query_from_string(cls, query: str) -> dict:
        # Preprocess the query string
        # Use regex to split alphanumeric strings into words and numbers
        words = re.findall(r'\d+|\D+', query.lower())

        # Further process each word
        processed_words = []
        for word in words:
            # Split non-numeric words by non-word characters
            if not word.isdigit():
                processed_words.extend(re.findall(r'\w+', word))
            else:
                processed_words.append(word)

        def create_flexible_regex(word):
            diacritic_map = {
                'a': '[aáàâãäåăąǎǟǡǻȁȃạảấầẩẫậắằẳẵặ]',
                'b': '[bḃḅḇƀɓ]',
                'c': '[cćĉċčçḉƈ]',
                'd': '[dďḋḍḏḑḓđɖɗ]',
                'e': '[eéèêëēĕėęěȅȇȩḕḗḙḛḝẹẻẽếềểễệ]',
                'f': '[fḟƒ]',
                'g': '[gćĝğġģǥǧǵḡɠ]',
                'h': '[hĥħḣḥḧḩḫẖ]',
                'i': '[iíìîïĩīĭįǐȉȋḭḯỉịĳ]',
                'j': '[jĵǰ]',
                'k': '[kķǩḱḳḵƙ]',
                'l': '[lĺļľḷḹḻḽłƚɫ]',
                'm': '[mḿṁṃɱ]',
                'n': '[nńņňṅṇṉṋñŋ]',
                'o': '[oóòôõöōŏőơǒǫǭȍȏṍṏṑṓọỏốồổỗộớờởỡợ]',
                'p': '[pṕṗƥ]',
                'q': '[q]',
                'r': '[rŕŗřȑȓṙṛṝṟ]',
                's': '[sśŝşšșṡṣṥṧṩ]',
                't': '[tţťṫṭṯṱțŧ]',
                'u': '[uúùûüũūŭůűųưǔǖǘǚǜȕȗṳṵṷṹṻụủứừửữự]',
                'v': '[vṽṿ]',
                'w': '[wŵẁẃẅẇẉ]',
                'x': '[xẋẍ]',
                'y': '[yýỳŷÿȳẏỵỷỹ]',
                'z': '[zźżžẑẓẕ]',
                'ae': '[æǣǽ]',
                'oe': '[œ]',
                'ue': '[ü]'
            }
            return ''.join(diacritic_map.get(c.lower(), re.escape(c)) for c in word)

        # Create a list of conditions for each word
        word_conditions = []
        for word in processed_words:
            word_condition = {"$or": [
                {key: {"$regex": f".*{create_flexible_regex(word)}.*", "$options": "iu"}}
                for key in (cls.all_fields() if cls.searchable is None else cls.searchable)
            ]}
            word_conditions.append(word_condition)

        # Combine all word conditions with $and
        mongo_query = {"$and": word_conditions} if word_conditions else {}
        return mongo_query

    @classmethod
    def find_by_id(cls: type[T], _id: str | ObjectId) -> Optional[T]:
        object_id = ObjectId(_id) if isinstance(_id, str) else _id
        return cls.find_one(cls._query({'_id': object_id}))

    @classmethod
    def find(cls: type[T], query: dict[str, any], **kwargs) -> list[T]:
        return [cls(**data) for data in (cls.collection_cls()).find(cls._query(query), **kwargs)]

    @classmethod
    def find_one(cls: type[T], query: dict[str, any], **kwargs) -> Optional[T]:
        data = (cls.collection_cls()).find_one(cls._query(query), **kwargs)
        return cls(**data) if data else None

    @classmethod
    def find_or_fail(cls: type[T], query: dict[str, any], **kwargs) -> T:
        instance = cls.find_one(cls._query(query), **kwargs)
        if not instance:
            raise HttpException('model_not_found', 404, message=f'Resource {cls.__name__} not found.')
        return instance

    @classmethod
    def find_by_id_or_fail(cls: type[T], _id: str | ObjectId) -> T:
        object_id = ObjectId(_id) if isinstance(_id, str) else _id
        return cls.find_or_fail(cls._query({'_id': object_id}))

    @classmethod
    def exists(cls, query: dict[str, any]) -> bool:
        return (cls.collection_cls()).count_documents(cls._query(query)) > 0

    @classmethod
    def first(cls: type[T], **kwargs) -> Optional[T]:
        data = (cls.collection_cls()).find_one(cls._query({}), **kwargs)
        return cls(**data) if data else None

    @classmethod
    def delete_many(cls, query: dict[str, any], **kwargs) -> None:
        (cls.collection_cls()).delete_many(cls._query(query), **kwargs)

    def delete(self) -> None:
        [observer.on_deleting(self) for observer in self.observers]
        (self.collection()).delete_one(self._query({'_id': self._id}))
        [observer.on_deleted(self) for observer in self.observers]

    @classmethod
    def delete_one(cls, query: dict[str, any], **kwargs) -> None:
        (cls.collection_cls()).delete_one(cls._query(query), **kwargs)

    @classmethod
    def update_many(cls, query: dict[str, any], data: dict[str, any]) -> None:
        # Initialize the update data with the updated_at field
        update_data = {"$set": {"updated_at": datetime.now()}}

        # Merge the provided data into the update_data
        for key, value in data.items():
            if key == "$set":
                # If the key is "$set", merge its contents with the existing "$set" in update_data
                if "$set" in update_data:
                    update_data["$set"].update(value)
                else:
                    update_data["$set"] = value
            else:
                # For other operations like "$unset", simply add/merge them
                update_data[key] = value

        (cls.collection_cls()).update_many(cls._query(query), update_data)

    def update(self: T, data: dict[str, any]) -> T:
        for key, value in data.items():
            self.clean[key] = self.get(key)
            setattr(self, key, value)
        self.save()
        return self

    @classmethod
    def count(cls, query: dict[str, any] = None, **kwargs) -> int:
        return (cls.collection_cls()).count_documents(cls._query(query), **kwargs)

    @classmethod
    def aggregate(cls, pipeline: list[dict[str, any]]) -> list[dict[str, any]]:
        cursor = (cls.collection_cls()).aggregate(pipeline)
        return cursor.to_list(length=None)

    @classmethod
    def insert_many(cls, data: list[dict[str, any]]) -> None:
        for d in data:
            d.update(cls._query({'created_at': datetime.now(), 'updated_at': datetime.now()}))

        (cls.collection_cls()).insert_many(data)

    @classmethod
    def update_or_create(cls: type[T], query: dict[str, any], data: dict[str, any]) -> T:
        instance = cls.find_one(cls._query(query))
        if instance:
            instance.update(data)
        else:
            instance = cls.create({**query, **data})
        return instance

    def is_dirty(self, key: str) -> bool:
        return key in self.clean

    # @property
    # def id(self) -> Optional[ObjectId]:
    #     return getattr(self, "_id", None)

    def get(self, key: str, default: any = None) -> any:
        return getattr(self, key, default) or default

    def set(self, key: str, value: any) -> None:
        if not self.is_dirty(key):
            self.clean[key] = self.get(key)
        setattr(self, key, value)

    @property
    def id(self) -> Optional[ObjectId]:
        return self._id

    def __setattr__(self, key: str, value: any) -> None:
        """Override the default setattr to track changes to the model."""
        if key in self.model_fields().keys():
            if not self.is_dirty(key):
                self.clean[key] = self.get(key)

        super().__setattr__(key, value)

    #    def __getattr__(self, name: str):
    # if name == "_id":
    #     return getattr(self, "id")
    # return super().__getattr__(name)

    # def dict(self) -> dict[str, any]:
    #    def convert_object_id(item):
    #         if isinstance(item, dict):
    #             return {k: convert_object_id(v) for k, v in item.items()}
    #         elif isinstance(item, list):
    #             return [convert_object_id(i) for i in item]
    #         elif isinstance(item, ObjectId):
    #             return str(item)
    #        return item

    #    return {key: convert_object_id(getattr(self, key)) for key in
    #            self.fillable + (['_id'] if hasattr(self, '_id') else [])}

    def dict(self, *args, **kwargs):
        """Override the default dict method."""
        data = {key: self.serialise(getattr(self, key)) for key in self.all_fields()}
        return data

    def serialise(self, val):
        if isinstance(val, ObjectId):
            return str(val)
        if isinstance(val, datetime):
            return val.isoformat()
        # insert serialisation here <start>

        # insert serialisation here <end>
        elif isinstance(val, list):
            return [self.serialise(item) for item in val]
        elif isinstance(val, dict):
            return {key: self.serialise(value) for key, value in val.items()}

        return val

    @classmethod
    def _update_or_create_text_index(cls):
        # Fetch existing text indexes
        collection = cls.collection_cls()
        existing_indexes = collection.index_information()

        # Check if current text index matches the desired fields
        current_text_index_fields = set()
        for index_name in existing_indexes:
            if "text" in existing_indexes[index_name].get('key', []):
                current_text_index_fields = {field[0] for field in existing_indexes[index_name]['key']}
                break

        fields = cls.all_fields()
        desired_fields_set = set(fields)
        if current_text_index_fields != desired_fields_set:
            # Drop existing text index
            for index_name in existing_indexes:
                if "text" in existing_indexes[index_name].get('key', []):
                    collection.drop_index(index_name)

            # Create new text index with desired fields
            collection.create_index([(field, TEXT) for field in fields], name=f"{cls.__name__.lower()}_text")

    @classmethod
    def _query(cls, query: dict = None) -> dict:
        query = query or {}

        ## insert query transformation here

        return query

    @classmethod
    def find_or_create(cls: type[T], query: dict, data: dict = None) -> T:
        if data is None:
            data = {}

        instance = cls.find_one(cls._query(query))
        if not instance:
            instance = cls.create(cls._query({**query, **data}))
        return instance