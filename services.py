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
from config import loop, KAFKA_BOOTSTRAP_SERVERS,  KAFKA_CONSUMER_GROUP_POST, KAFKA_TOPIC_POST, KAFKA_CONSUMER_GROUP_USER, KAFKA_TOPIC_USER
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import json
# It provides password hashing and verification utilities.
import passlib.hash as _hash

_JWT_SECRET = "thisisnotverysafe"




if TYPE_CHECKING:
    from sqlalchemy.orm import Session



def _add_tables():
# >>>import services
# >>> services._add_tables()
# Helper function responsible for creating the database tables based on the SQLAlchemy models defined in the database module.
    return _database.Base.metadata.create_all(bind=_database.engine)



def get_db():
    # It is a FastAPI dependency that provides a database session (db) to other routes and functions.
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()



async def consume():
    # consuming what what sent from post_microservice post_microservice ->> users

    # Obtain the database session or transaction object from the dependency injection system
    db_session = _database.SessionLocal()

    # Create a Kafka consumer instance
    consumer = AIOKafkaConsumer(KAFKA_TOPIC_USER,loop=loop, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, group_id= KAFKA_CONSUMER_GROUP_USER)
    await consumer.start()
    
    try:
        # Consume messages from the Kafka topic
        async for postProduced in consumer:
            # Decode the message value from bytes to a JSON strin
            value_json = postProduced.value.decode('utf-8')
            
            # Convert the JSON string to a dictionary
            post_dict = json.loads(value_json)

            # Check if the user_stats object exists in the database
            user_stats = db_session.query(_models.UserStats).filter(_models.UserStats.user_id == post_dict['owner_id']).first()
            
            if user_stats is None:
                # If the user_stats object doesn't exist, create a new instance
                user_stats_db_obj = _models.UserStats(user_id = int(post_dict['owner_id']), post_count=1)
                db_session.add(user_stats_db_obj)
                db_session.commit()
                db_session.refresh(user_stats_db_obj)
            else:
                # If the user_stats object exists, increment the post_count
                user_stats.post_count +=1
                db_session.commit()

    finally:
        db_session.close()
        await consumer.stop()







async def get_user_by_email(email: str, db: _orm.Session):
    # Asynchronous function that retrieves a user from the database based on the provided email address.
    return db.query(_models.User).filter(_models.User.email == email).first()



async def create_user(user: _schemas.UserCreate, db:_orm.Session):
    try:
        # Validate the email address
        valid = _email_val.validate_email(email=user.email)
        email = valid.ascii_email
    except _email_val.EmailNotValidError:
        raise _fastapi.HTTPException(
            status_code=404,
            detail="Please enter a valid email"
        )
    
    # Hash the user's password
    hashed_password = _hash.bcrypt.hash(user.password)

    # Create a new user object
    user_obj = _models.User(email = email, hashed_password = hashed_password, first_name = user.first_name, last_name= user.last_name)

    #Add the user to the database
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    return user_obj
 

async def produce_user_info(user: _schemas.UserProducer, db: _orm.Session):
    # Create a Kafka producer instance  user_info ->> Post_microservice
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
        await producer.send_and_wait(topic=KAFKA_TOPIC_POST, value=value_json)

    finally:
        # Stop the producer to release resources
        await producer.stop()





async def create_token(user: _models.User):
    # Create a JWT token based on the user data
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
    # Make sure credentials are found in users table
    user = await get_user_by_email(email = credentials.email, db=db)

    if not user:
        # User Not Regestered inturn doesnt have access to login functionality
        raise _fastapi.HTTPException(
            status_code=404,
            detail="User not Found. Please Regeister to Login"
            )
    # User credentials exist in db, but compare and verify matching hashed passwords
    if not _hash.bcrypt.verify(credentials.password_txt, user.hashed_password):
        raise _fastapi.HTTPException(
            status_code=401,
            detail="Invalid Credentials"
        )
    return user
    





