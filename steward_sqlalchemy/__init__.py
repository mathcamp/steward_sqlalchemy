""" Steward extension that adds sqlalchemy """
import sqlalchemy.ext.declarative
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

# pylint: disable=F0401,E0611
from zope.sqlalchemy import ZopeTransactionExtension
# pylint: enable=F0401,E0611

from .mixins import SelfAwareModel, JsonableMixin, ModelEqualityMixin


__base__ = sqlalchemy.ext.declarative.declarative_base()

__all__ = ['declarative_base', 'SelfAwareModel', 'JsonableMixin',
           'ModelEqualityMixin']


def declarative_base():
    """ Retrieve the global declarative base class """
    return __base__


def _db(request):
    """ Access a sqlalchemy session """
    maker = request.registry.dbmaker
    session = maker()

    def cleanup(request):
        """ Close the session after the request """
        session.close()
    request.add_finished_callback(cleanup)

    return session


def create_schema(registry):
    """
    Create the database schema if needed

    Parameters
    ----------
    registry : dict
        The configuration registry

    Notes
    -----
    The method should only be called after importing all modules containing
    models which extend the ``Base`` object.

    """
    __base__.metadata.create_all(bind=registry.dbmaker.kw['bind'])


def drop_schema(registry):
    """
    Drop the database schema

    Parameters
    ----------
    registry : dict
        The configuration registry

    Notes
    -----
    The method should only be called after importing all modules containing
    models which extend the ``Base`` object.

    """
    __base__.metadata.drop_all(bind=registry.dbmaker.kw['bind'])


class DatabaseTaskMixin(object):

    """ Celery task mixin with sqlalchemy session """
    _sessionmaker = None
    _db = None

    @property
    def db(self):
        """ Get the database session object """
        if self._sessionmaker is None:
            engine = engine_from_config(self.config.settings,
                                        prefix='sqlalchemy.')
            self._sessionmaker = sessionmaker(bind=engine)
        if self._db is None:
            self._db = self._sessionmaker()

            def cleanup(task, status, retval, task_id, args, kwargs, einfo):
                """ Close the session after the task """
                if einfo is None:
                    task.db.commit()
                else:
                    task.db.rollback()
            self.callbacks.append(cleanup)
        return self._db


def include_tasks(config):
    """ Add tasks """
    config.mixins.append(DatabaseTaskMixin)


def includeme(config):
    """ Configure the app """
    settings = config.get_settings()
    config.add_request_method(_db, name='db', reify=True)
    engine = engine_from_config(settings, prefix='sqlalchemy.')
    config.registry.dbmaker = sessionmaker(bind=engine,
                                           extension=ZopeTransactionExtension())
    config.registry.subrequest_methods.append('db')
