
# It defines the Pydantic schemas used for data validation and serialization.
import datetime as _dt
import pydantic as _pydantic


class _UserBase(_pydantic.BaseModel):
    # id and date created are immutable, and will not be found when donig post
    first_name : str
    last_name : str
    email : str
    
    
class User(_UserBase):
    id: int
    date_created: _dt.datetime
    class Config:
        orm_mode=True



class UserLogin(_pydantic.BaseModel):
    email: str
    password_txt: str


class UserCreate(_UserBase):
    password: str


class UserProducer(_pydantic.BaseModel):
    id : int
    first_name: str
    last_name :str


