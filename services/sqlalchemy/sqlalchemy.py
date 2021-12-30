"""Settings of SQLAlchemy"""

# Retic
from retic import App

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

# Services
from services.sqlalchemy.base import Base

# Models
from models import *

# Constants
"""Define all options"""
OPTIONS_URI = {
    u'drivername': App.config.get("MYSQL_DRIVERNAME"),
    u'host': App.config.get("MYSQL_HOST"),
    u'port': App.config.get("MYSQL_PORT", callback=int),
    u'username': App.config.get("MYSQL_USERNAME"),
    u'password': App.config.get("MYSQL_PASSWORD"),
    u'database': App.config.get("MYSQL_DATABASE"),
    u'query': App.config.get("MYSQL_QUERY"),
}
OPTIONS_ENGINE = {
    u"echo": App.config.get("MYSQL_ECHO", callback=bool),
    u"pool_pre_ping": App.config.get("MYSQL_POOL_PREPING", callback=bool),
    u"pool_size": App.config.get("MYSQL_POOL_SIZE", callback=int),
    u"max_overflow": App.config.get("MYSQL_MAX_OVERFLOW", callback=int),
}


def config_sqlalchemy():
    """Define the URI"""
    _database_uri = URL(**OPTIONS_URI)

    """Define the Engine
    https://docs.sqlalchemy.org/en/13/core/engines.html
    """
    _engine = create_engine(_database_uri, **OPTIONS_ENGINE)

    """delete all models and create all models again
    https://docs.sqlalchemy.org/en/13/core/metadata.html
    """

    """"Initialize all database"""
    # initialize(_engine)

    """Define the session"""
    _sessionmaker = sessionmaker(_engine)
    return _sessionmaker


def initialize(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
