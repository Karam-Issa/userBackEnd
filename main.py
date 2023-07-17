import fastapi as _fastapi
from fastapi import Header
from typing import List
import fastapi.security as _security
import sqlalchemy.orm as _orm
import schemas as _schemas
import services as _services
import jwt
import asyncio
_JWT_SECRET = "thisisnotverysafe"

app = _fastapi.FastAPI()

# Create a background task to consume messages from Kafka
asyncio.create_task(_services.consume())


@app.post("/api/v1/regester")
async def create_user(user: _schemas.UserCreate,
                       db: _orm.Session = _fastapi.Depends(_services.get_db)):
    # Check if the user with the same email already exists in the database
    db_user = await _services.get_user_by_email(email= user.email, db=db)

    if db_user:
        raise _fastapi.HTTPException(
            status_code=400,
            detail="User with that email already exists"
        )
    
    # Create the user if not already found in the db
    user = await _services.create_user(user=user, db=db)

    # Produce user information to Kafka POST_SIDE
    await _services.produce_user_info(
        _schemas.UserProducer(id=user.id, first_name=user.first_name, last_name=user.last_name),
        db=db
        )

    return user


@app.post("/api/v1/login")
async def login_user(credentials: _schemas.UserLogin,db: _orm.Session = _fastapi.Depends(_services.get_db)):
    # Authenticate the user based on the provided credentials
    user = await _services.authenticate_user(credentials=credentials, db=db)
    if not user:
        raise _fastapi.HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    # Create a JWT token for the authenticated user
    token = await _services.create_token(user=user)

    # Include the token in the response headers
    headers = {"Authorization": f"Bearer {token}"}
    return _fastapi.Response(headers=headers)
    

@app.get("/api/v1/user", response_model=_schemas.User)
async def get_user_info(authorization: str = Header(), db: _orm.Session = _fastapi.Depends(_services.get_db)):
    # Extract the JWT token from the authorization header
    jwt_token = authorization.split("Bearer ")[1]
    
    try:
        # Decode the JWT token using the secret key
        decoded_token = jwt.decode(jwt_token, _JWT_SECRET, algorithms=["HS256"])

        # Get the user email from the decoded token
        user_email = decoded_token["email"]

        # Retrieve the user from the database based on the email
        user = await _services.get_user_by_email(email=user_email, db=db)

        if not user:
            raise _fastapi.HTTPException(
                status_code=404,
                detail="User not found"
            )

        return user
    
    except jwt.exceptions.DecodeError:
        raise _fastapi.HTTPException(
            status_code=401,
            detail="Invalid JWT token"
        )
