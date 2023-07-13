import fastapi as _fastapi
from fastapi import Header
from typing import List
import fastapi.security as _security
import sqlalchemy.orm as _orm
import schemas as _schemas
import services as _services
import jwt
import requests
 #testing git
app = _fastapi.FastAPI()
_JWT_SECRET = "thisisnotverysafe"
@app.post("/api/v1/regester")
async def create_user(user: _schemas.UserCreate,
                       db: _orm.Session = _fastapi.Depends(_services.get_db)):
    db_user = await _services.get_user_by_email(email= user.email, db=db)
    if db_user:
        raise _fastapi.HTTPException(
            status_code=400,
            detail="User with that email already exists"
        )
    #Create the user if not already found in the db
    user = await _services.create_user(user=user, db=db)    

    
    

    return user


@app.post("/api/v1/login")
async def login_user(credentials: _schemas.UserLogin,db: _orm.Session = _fastapi.Depends(_services.get_db)):
    user = await _services.authenticate_user(credentials=credentials, db=db)
    if not user:
        raise _fastapi.HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    token = await _services.create_token(user=user)
    #return token
    headers = {"Authorization": f"Bearer {token}"}
    return _fastapi.Response(headers=headers)
    


@app.get("/api/v1/user", response_model=_schemas.User)
async def get_user_info(authorization: str = Header(), db: _orm.Session = _fastapi.Depends(_services.get_db)):
    
    jwt_token = authorization.split("Bearer ")[1]
    
    try:
       
        decoded_token = jwt.decode(jwt_token, _JWT_SECRET, algorithms=["HS256"])

        
        user_email = decoded_token["email"]

        
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



       