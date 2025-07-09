from functools import wraps
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.observers.observer_base import ObserverBase


def register_observer(observer_cls):
    def decorator(model_cls):
        original_init = model_cls.__init__

        @wraps(original_init)
        def new_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            self.register_observer(observer_cls())

        model_cls.__init__ = new_init
        return model_cls
    return decorator


class HasObservers:
    def __init__(self, *args, **kwargs):
        self.observers: list[ObserverBase] = []

    def register_observer(self, observer):
        """Register an observer for this model."""
        self.observers.append(observer)
