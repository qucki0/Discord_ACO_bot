from pydantic import BaseModel


class PropertyModel(BaseModel):
    def __setattr__(self, key, val):
        method = self.__config__.property_set_methods.get(key)
        if method is None:
            super().__setattr__(key, val)
        else:
            getattr(self, method)(val)

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
