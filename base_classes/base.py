import abc
import asyncio

from pydantic import BaseModel


class PropertyModel(BaseModel):
    def __setattr__(self, key, val):
        method = self.__config__.property_set_methods.get(key)
        if method is None:
            super().__setattr__(key, val)
        else:
            func = getattr(self, method)
            if asyncio.iscoroutinefunction(func):
                asyncio.get_running_loop().create_task(func(val))
            else:
                func(val)

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        new_data = {}
        for key in data:
            if key.endswith("_"):
                new_key = key[::-1].replace("_", "", 1)[::-1]
                new_data[new_key] = data[key]
            else:
                new_data[key] = data[key]
        return new_data


class SingletonBase:
    __instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super().__new__(cls)
        return cls.__instances[cls]


class AsyncObject:

    @abc.abstractmethod
    async def __ainit__(self):
        """ Async constructor, you should implement this """

    async def __initobj(self):
        """ Crutch used for __await__ after spawning """

        await self.__ainit__()  # pass the parameters to __ainit__ that passed to __init__
        return self

    def __await__(self):
        return self.__initobj().__await__()

    def __init_subclass__(cls, **kwargs):
        assert asyncio.iscoroutinefunction(cls.__ainit__)  # __ainit__ must be async
