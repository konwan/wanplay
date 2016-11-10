import hashlib
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref


"""
SQLAlchemy 使用了稱為 Declarative system 的類別，用來映對 Python 類別與資料庫表格之間的關聯，
所以 User 類別繼承了 Base ，而且又需要在 User 類別中定義 __tablename__ 屬性的值，代表它映對到資料庫中的 users 資料表。
如果把 Declarative system 想像成 Python 類別介接資料庫的接線生就會相對較好理解，
也因此 User 類別需要繼承 Base 才能夠讓 Declarative system 了解表格的欄位名稱、型態、長度以及相對應的 Python 類別。
通常一個應用程式也只會用到一個 declarative_base() 類別。

定義表格的內容，被稱為 Table metadata，而 User 類別則稱為 Mapped class ，
若想知道一個實例映對的資料表名稱與 Python 類別名稱，則可以試著存取 __mapper__ 屬性。
資料表格欄位沒有指定長度，這在 SQLite, PostgreSQL 中是合法的，被稱為 minimal table descriptiopn ，
而有指定長度的情況就是 full table description 

僅止於建立資料庫 Engine、定義資料基模(scheme)。
要真正與資料庫進行互動(新增、刪除、修改)就得建立 Session 進行。

 __init__ 與 __repr__ 兩個 Python 預設類別方法。
在 SQLAlchemy 這兩個方法是可以省略不寫的。如果沒有覆寫(override) __init__ 的話，
SQLAlchemy 自行預設的 __init__ 就會把所有欄位列為 __init__ 的參數
使用 ORM 過程就是定義資料庫表格、撰寫資料庫表格對應的 Python 類別、設定資料庫表格與其他資料庫表格間的關聯等動作。

"""
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
    """
    在 SQLAlchemy 的實做過程中，使用了Python 標準的 logging 模組進行開發，
    因此想要察看 SQLAlchemy 的執行過程的訊息就可以加上參數 echo=True，
    就可以看到 SQL 的指令與相關訊息。
    而 engine 是 SQLAlchemy 的 Engine 實例(instance)， Engine 則是可以視為用來介接主要的資料庫(MySQL, SQLite, ...)的介面。
    建立 Engine 實例時，實際是還沒真正連接到資料庫的，只有在第一個工作或 SQL 指令被下達，它才會真正連接到資料庫執行。
    """
    engine = create_engine('sqlite:///:memory:', echo=True)

    # create table
    """
    
    在資料庫內建立起相對應的 users 表格。這個用來建立相對應表格以及建立與 Python 類別間的動作，是由 metadata 負責的。
    建立一個 User 類別的實例，並且列印出其所對應的 Python 類別與資料庫表格名稱，
    其結果為 Mapper|User|user 代表 User 類別映對到 user 資料表。
    此外，需要注意的是截至目前為止這筆資料仍尚未寫進資料庫內。
    """
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
