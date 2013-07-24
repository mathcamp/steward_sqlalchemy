""" Steward extension that adds sqlalchemy """
import json
from sqlalchemy import engine_from_config
import sqlalchemy.ext.declarative
from sqlalchemy.orm import sessionmaker
#pylint: disable=F0401,E0611
from zope.sqlalchemy import ZopeTransactionExtension
#pylint: enable=F0401,E0611


__base__ = sqlalchemy.ext.declarative.declarative_base()

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

def includeme(config):
    """ Configure the app """
    settings = config.get_settings()
    config.add_request_method(_db, name='db', reify=True)
    engine = engine_from_config(settings, prefix='sqlalchemy.')
    config.registry.dbmaker = sessionmaker(bind=engine,
                                           extension=ZopeTransactionExtension())
    config.registry.subrequest_methods.append('db')
