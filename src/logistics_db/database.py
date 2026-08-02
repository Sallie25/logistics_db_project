from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from logistics_db.config import settings


class Base(DeclarativeBase):
    pass
    


# TODO: creating the SQLALCHEMY engine using the settings.database_url 
engine = create_engine(settings.database_url(), echo = True)

# TODO: creating a session factory that binds to the engine
Session = sessionmaker(bind = engine)
