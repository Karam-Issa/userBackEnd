import datetime as _dt
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import passlib.hash as _hash
import database as _database
from database import Base

class User(Base):
    __tablename__= "users"
    id =_sql.Column(_sql.Integer, primary_key=True, index=True)
    first_name = _sql.Column(_sql.String,index=True)
    last_name = _sql.Column(_sql.String,index=True)
    email= _sql.Column(_sql.String,index=True, unique=True)
    hashed_password = _sql.Column(_sql.String)
    date_created = _sql.Column(_sql.String, default=_dt.datetime.utcnow)





