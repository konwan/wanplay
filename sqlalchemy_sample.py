import hashlib
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

class User(Base):
    # crear table
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)

    def __init__(self, name, username, password):
        self.name = name
        # self.password = hashlib.sha1(password).hexdigest()

    def __repr__(self):
        return "User('%s','%s', '%s')" % (self.name, self.username, self.password)


if __name__ == '__main__':
    # create engine but not set up data yet, when 1st sql execute it will contect database
    engine = create_engine('sqlite:///:memory:', echo=True)

    # create table
    Base.metadata.create_all(engine)

    u1 = User("cindy","username","cindy")
    print ("Mapper:", u1.__mapper__)

    """ success info
    2016-11-10 16:34:17,782 INFO sqlalchemy.engine.base.Engine SELECT CAST('test plain returns' AS VARCHAR(60)) AS anon_1
    2016-11-10 16:34:17,783 INFO sqlalchemy.engine.base.Engine ()
    2016-11-10 16:34:17,783 INFO sqlalchemy.engine.base.Engine SELECT CAST('test unicode returns' AS VARCHAR(60)) AS anon_1
    2016-11-10 16:34:17,783 INFO sqlalchemy.engine.base.Engine ()
    2016-11-10 16:34:17,784 INFO sqlalchemy.engine.base.Engine PRAGMA table_info("users")
    2016-11-10 16:34:17,784 INFO sqlalchemy.engine.base.Engine ()
    2016-11-10 16:34:17,785 INFO sqlalchemy.engine.base.Engine
    CREATE TABLE users (
        id INTEGER NOT NULL,
        name VARCHAR,
        password VARCHAR,
        PRIMARY KEY (id)
    )


    2016-11-10 16:34:17,785 INFO sqlalchemy.engine.base.Engine ()
    2016-11-10 16:34:17,786 INFO sqlalchemy.engine.base.Engine COMMIT
    Mapper: Mapper|User|users
    """
