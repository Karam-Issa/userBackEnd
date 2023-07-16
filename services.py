import database as _database
import fastapi as _fastapi
import models as _models
import schemas as _schemas
import fastapi.security as _security
from typing import TYPE_CHECKING, List
import sqlalchemy.orm as _orm
# It is used for validating email addresses.
import email_validator as _email_val
#  It is used for encoding and decoding JSON Web Tokens 
import jwt
import jwt.exceptions 
from config import loop, KAFKA_BOOTSTRAP_SERVERS,  KAFKA_CONSUMER_GROUP, KAFKA_TOPIC
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import json
# It provides password hashing and verification utilities.
import passlib.hash as _hash

_JWT_SECRET = "thisisnotverysafe"




if TYPE_CHECKING:
    from sqlalchemy.orm import Session


# >>>import services
# >>> services._add_tables()
# it is a helper function responsible for creating the database tables based on the SQLAlchemy models defined in the database module.
def _add_tables():
    return _database.Base.metadata.create_all(bind=_database.engine)


# It is a FastAPI dependency that provides a database session (db) to other routes and functions.
def get_db():
    db = _database.SessionLocal()

    try:
        yield db
    finally:
        db.close()


# Asynchronous function that retrieves a user from the database based on the provided email address.
async def get_user_by_email(email: str, db: _orm.Session):
    return db.query(_models.User).filter(_models.User.email == email).first()



async def create_user(user: _schemas.UserCreate, db:_orm.Session):

    # cehck that the email is valid 
    try:
        valid = _email_val.validate_email(email=user.email)

        email = valid.ascii_email

    except _email_val.EmailNotValidError:
        raise _fastapi.HTTPException(
            status_code=404,
            detail="Please enter a valid email"
        )
    hashed_password = _hash.bcrypt.hash(user.password)
    user_obj = _models.User(email = email, hashed_password = hashed_password, first_name = user.first_name, last_name= user.last_name)

    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj
 

async def produce_user_info(user: _schemas.UserProducer, db: _orm.Session):
    # Create a Kafka producer instance
    producer = AIOKafkaProducer(loop=loop, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    try:
        
        # Convert the object attributes to a dictionary
        user_dict = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name
        }

        # Convert the dictionary to a JSON string and encode as bytes
        value_json = json.dumps(user_dict).encode('utf-8')

        # Send the message to the Kafka topic
        await producer.send_and_wait(topic=KAFKA_TOPIC, value=value_json)
    finally:
        # Stop the producer to release resources
        await producer.stop()

async def create_token(user: _models.User):
    user_schema_obj = _schemas.User.from_orm(user)
    user_dict = user_schema_obj.dict()
    del user_dict["date_created"]

    try:
        token = jwt.encode(user_dict, _JWT_SECRET)
    except:
        raise _fastapi.HTTPException(
            status_code=500,
            detail="Failed to generate Token"
        )
    
    return token



async def authenticate_user(credentials: _schemas.UserLogin, db:_orm.Session):
    user = await get_user_by_email(email = credentials.email, db=db)
    if not user:
        raise _fastapi.HTTPException(
            status_code=404,
            detail="User not Found. Please Regeister to Login"
            )
    if not _hash.bcrypt.verify(credentials.password_txt, user.hashed_password):
        raise _fastapi.HTTPException(
            status_code=401,
            detail="Invalid Credentials"
        )
    return user
    





