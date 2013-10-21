""" Useful mixins for models """
import inspect

from sqlalchemy.orm.attributes import InstrumentedAttribute


class SelfAwareModel(object):

    """ Provide a useful method to get all sqlalchemy columns of a class """

    @classmethod
    def _columns(cls):
        """ Get the names of all attributes that are SQL columns """
        columns = []
        for name, member in inspect.getmembers(cls):
            if (not name.startswith('_') and
                    isinstance(member, InstrumentedAttribute)):
                columns.append(name)
        return columns

    @classmethod
    def _primary_key_columns(cls):
        """ Get the names of all attributes that are primary key columns """
        return [col for col in cls._columns() if getattr(cls, col).primary_key]


class ModelEqualityMixin(SelfAwareModel):

    """
    A mixin that provides __hash__ and __eq__ methods

    The hash and equality are calculated based on the columns of the model that
    are marked as primary keys

    """

    def __hash__(self):
        return sum([hash(getattr(self, key)) for key in
                    self.__class__._primary_key_columns()])

    def __eq__(self, other):
        return all([getattr(self, key) == getattr(other, key) for key in
                    self.__class__._primary_key_columns()])


class JsonableMixin(SelfAwareModel):

    """
    A mixin that provides json serialization/deserialization methods

    The json serialization is done by adding a __json__ method that can be
    called by a default handler for json.dump. The logic is actually in
    _json(), so if you need to customize the behavior you may override the
    __json__() method and still call _json().

    The deserialization logic in load just passes all key-value pairs in the
    dictionary to the __init__ method. Override it for custom behavior.

    """

    def _json(self, exclude=()):
        """ Return a dictionary of all column attributes """
        return {name: getattr(self, name) for name in self._columns()
                if name not in exclude}

    def __json__(self, request=None):
        return self._json()

    @classmethod
    def load(cls, data):
        """ Load this object from json data """
        return cls(**data)

    @classmethod
    def load_all(cls, data):
        """ Load a list of json data objects """
        return [cls.load(obj) for obj in data]
