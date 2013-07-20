Steward SQLAlchemy
==================
This is a Steward extension for using sqlalchemy.

Setup
=====
Steward_sqlalchemy depends on pyramid_tm. To use steward_sqlalchemy, just add
it to your includes either programmatically::

    config.include('pyramid_tm')
    config.include('steward_sqlalchemy')

or in the config.ini file::

    pyramid.includes = pyramid_tm
    pyramid.includes = steward_sqlalchemy

Usage
=====
After inclusion, you can access the sqlalchemy session on the request object::

    def handle_request(request):
        obj = request.db.query(MyDBObj).one()
        return obj.value

Configuration
=============
::

    # The SQLAlchemy database url (required)
    sqlalchemy.url = sqlite:///%(here)s/steward.sqlite
