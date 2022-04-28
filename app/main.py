from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from . import database


from app.Oauth2 import create_access_token
from .import schemas, models
from sqlalchemy.orm import Session
from .utils import  token_utils,database_utils,mailer_utils
from starlette.requests import Request
from .database import get_db, engine


from .config import settings

models.Base.metadata.create_all(bind= engine)

app= FastAPI()


frontend_url = 'http://test.com/'


@app.post('/register/',status_code= status.HTTP_201_CREATED, response_model=schemas.RegistrationUserRepsonse)
async def register(request:Request,user_credentials:schemas.UserCreate,  db:Session = Depends(get_db)):
    email_check = db.query(models.User).filter(models.User.email ==user_credentials.email).first()
    if email_check !=None:
       raise HTTPException(
        detail='Email is already registered',
        status_code= status.HTTP_409_CONFLICT
       )

      # hash the password

    hashed_password =     database_utils.get_password_hashed(user_credentials.password)
    user_credentials.password = hashed_password

    new_user = models.User(
    email = user_credentials.email,
    password = user_credentials.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = token_utils.token(user_credentials.email)
    # print(token)
    email_verification_endpoint = f'{frontend_url}auth/confirm-email/{token}/'
    mail_body = {

        'email':user_credentials.email,
        'project_name': settings.project_name,
        'url': email_verification_endpoint
    }


    
    mail_status =await mailer_utils.send_email_async(subject="Email Verification: Registration Confirmation",
    email_to=user_credentials.email, body=mail_body, template='email_verification.html')
  
    return {

    "message": "User registration successful",
    "data": new_user
    }
    
    
    
@app.post('/login/', status_code=status.HTTP_200_OK)
async def login(request:Request,user_credentials:OAuth2PasswordRequestForm= Depends(),db:Session = Depends(database.get_db)):

    # Filter search for user
    user = db.query(models.User).filter(models.User.email== user_credentials.username).first()


    if not user:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "Invalid Username or Password",
            headers={"WWW-Authenticate":"Bearer"}
        )
    if user.is_verified != True:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail= "Account Not Verified"
        )

    access_token = create_access_token(data={'user_id':user.id})
    return {
        'access_token':access_token,
        'token_type': 'bearer'
    }




@app.post('/confirm-email/{token}/', status_code=status.HTTP_202_ACCEPTED)
async def user_verification(token:str, db:Session=Depends(get_db)):

        
    token_data = token_utils.verify_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail= "Token for Email Verification has expired."
        )
    
    user = db.query(models.User).filter(models.User.email==token_data['email']).first()
    if not user:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f"User with email {user.email} does not exist"
        )
    user.is_verified = True
    db.add(user)
    db.commit()
    db.refresh(user)
    print(user)

    return {
        'message':'Email Verification Successful',
        'status':status.HTTP_202_ACCEPTED
    }





@app.post('/resend-verification/', status_code=status.HTTP_201_CREATED)
async def send_email_verfication(email_data:schemas.EmailSchema,request:Request,db:Session=Depends(database.get_db)):
 

    user_check = db.query(models.User).filter(models.User.email ==email_data.email).first()
    if not user_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail= "User information does not exist")
    
    token = token_utils.token(email_data.email)
    # print(token)
    email_verification_endpoint = f'{frontend_url}auth/confirm-email/{token}/'
    mail_body = {

        'email':user_check.email,
        'project_name': settings.project_name,
        'url': email_verification_endpoint
    }

    mail_status =await mailer_utils.send_email_async(
    subject="Email Verification: Registration Confirmation",
    email_to=user_check.email, body=mail_body, template='email_verification.html'
    
    )
    if mail_status == True:
        return {
            "message":"mail for Email Verification has been sent, kindly check your inbox.",
            "status": status.HTTP_201_CREATED
        }
    else:
        return {
            "message":"mail for Email Verification failled to send, kindly reach out to the server guy.",
            "status": status.HTTP_503_SERVICE_UNAVAILABLE
        }

