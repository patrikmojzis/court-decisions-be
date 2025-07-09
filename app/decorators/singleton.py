"""
Singleton decorator for ensuring only one instance of a class exists.
"""

import threading
from typing import TypeVar, Type, Dict, Any

T = TypeVar('T')

def singleton(cls: Type[T]) -> Type[T]:
    """
    Singleton decorator that ensures only one instance of a class exists.
    
    This decorator modifies the class's __new__ method to implement singleton behavior.
    It's thread-safe and supports classes with custom __new__ methods.
    
    Args:
        cls: The class to make a singleton
        
    Returns:
        The modified class with singleton behavior
        
    Example:
        @singleton
        class MyService:
            def __init__(self):
                self.data = "initialized"
        
        # Both instances will be the same object
        service1 = MyService()
        service2 = MyService()
        assert service1 is service2
    """
    instances: Dict[Type[Any], Any] = {}
    lock = threading.Lock()
    original_new = cls.__new__
    
    def __new__(cls_inner: Type[T], *args, **kwargs) -> T:
        # Double-checked locking pattern for thread safety
        if cls_inner not in instances:
            with lock:
                if cls_inner not in instances:
                    # Handle both custom and default __new__ methods
                    if original_new is object.__new__:
                        instance = original_new(cls_inner)
                    else:
                        instance = original_new(cls_inner, *args, **kwargs)
                    instances[cls_inner] = instance
        
        return instances[cls_inner]
    
    # Replace the class's __new__ method
    cls.__new__ = __new__  # type: ignore
    
    return cls 