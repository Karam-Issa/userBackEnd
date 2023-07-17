
# It defines the Pydantic schemas used for data validation and serialization.
import datetime as _dt
import pydantic as _pydantic


class _UserBase(_pydantic.BaseModel):
    # Base schema for user data
    # id and date created are immutable, and will not be found when donig post
    first_name : str
    last_name : str
    email : str
    
    
class User(_UserBase):
    # Schema for user data including additional fields
    id: int
    date_created: _dt.datetime
    class Config:
        orm_mode=True



class UserLogin(_pydantic.BaseModel):
    # Schema for user login credentials
    email: str
    password_txt: str


class UserCreate(_UserBase):
    # Schema for creating a new user
    password: str


class UserProducer(_pydantic.BaseModel):
    # Schema for kafka producer (information hiding and effieciency)
    id : int
    first_name: str
    last_name :str


