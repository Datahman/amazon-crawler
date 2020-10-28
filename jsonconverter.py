# import json


# class JsonConvert(object):
#     mappings = {}

#     @classmethod
#     def class_mapper(clsself, d):
#         for keys, cls in clsself.mappings.items():
#             if keys.issuperset(d.keys()):   # are all required arguments present?
#                 return cls(**d)
#         else:
#             # Raise exception instead of silently returning None
#             raise ValueError(
#                 'Unable to find a matching class for object: {!s}'.format(d))

#     @classmethod
#     def complex_handler(cls, Obj):
#         if hasattr(Obj, '__dict__'):
#             return Obj.__dict__
#         else:
#             raise TypeError('Object of type %s with value of %s is not JSON serializable' % (
#                 type(Obj), repr(Obj)))

#     @classmethod
#     def register(clsself, cls):
#         clsself.mappings[frozenset(
#             tuple([attr for attr, val in cls().__dict__.items()]))] = cls
#         return cls

#     @classmethod
#     def to_json(cls, obj):
#         return json.dumps(obj.__dict__, default=cls.complex_handler, indent=4)

#     @classmethod
#     def from_json(cls, json_str):
#         return json.loads(json_str.content.decode('utf-8'), object_hook=cls.class_mapper)
