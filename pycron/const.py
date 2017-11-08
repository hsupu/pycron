# import collections
#
#
# class Constant(object):
#
#     def __init__(self):
#         self.__frozen = False
#
#     def freeze(self):
#         self.__frozen = True
#
#     def __setattr__(self, name, value):
#         if name in self.__dict__:
#             raise TypeError('Constant cannot be changed')
#
#         if self.__frozen:
#             raise TypeError('Constant has been frozen')
#
#         if not isinstance(value, collections.Hashable):
#             if isinstance(value, list):
#                 value = tuple(value)
#             elif isinstance(value, set):
#                 value = frozenset(value)
#             elif isinstance(value, dict):
#                 raise TypeError('dict can not be used as constant')
#             else:
#                 raise ValueError('Mutable or custom type is not supported')
#         self.__dict__[name] = value
#
#     def __delattr__(self, name):
#         if name in self.__dict__:
#             raise TypeError('Constanst can not be deleted')
#         raise NameError("name '%s' is not defined" % name)
#
#     def __call__(self):
#         return self.__dict__


class Constant:
    def __init__(self, value=None):
        self.value = value

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        raise ValueError("Constant cannot be changed")

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return repr(self.value)


class ConstantEnum:
    @classmethod
    def entries(cls):
        fields = cls.__dict__
        items = {}
        for key in fields:
            if not key.startswith('_'):
                items[key] = fields[key]
        return items
