from pydantic import BaseModel, EmailStr
from datetime import datetime



class UserBase(BaseModel):
   email: EmailStr
   password:str
   is_verified: bool=False

class UserCreate(UserBase):
    pass

class UserLogin(BaseModel):
    email:EmailStr
    password: str

class UserResponse(BaseModel):
    id:int
    email:EmailStr
    created_at:datetime
   
    class Config:
       orm_mode = True

class RegistrationUserRepsonse(BaseModel):
    message:str
    data: UserResponse
    
    
class EmailSchema(BaseModel):
    email:EmailStr