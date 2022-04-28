from datetime import timedelta, datetime
from jose import JWTError, jwt



from .config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from . import schemas, models
from .database import get_db

from sqlalchemy.orm import Session

# Oauth2 set up
SECRET_KEY = settings.secret_key
ALGORITHM= settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES= settings.access_token_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login/')

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp':expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token:str, credential_exception):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        id:str = payload.get('user_id')
        if id is None:
            raise credential_exception
        
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credential_exception
    return token_data



async def get_current_user(token:str =Depends(oauth2_scheme), db:Session =Depends(get_db) ):
    credentials_exception = HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers ={"WWW-Authenticate": "Bearer"}
    )
    token = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id==token.id).first()
    return user



