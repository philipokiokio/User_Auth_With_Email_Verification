from re import TEMPLATE
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi_mail.email_utils import DefaultChecker
from app.schemas import EmailStr
from pathlib import Path
from dotenv import load_dotenv
import os
from fastapi_mail.errors import ConnectionErrors


load_dotenv()
config = ConnectionConfig(
    MAIL_USERNAME=os.getenv('MAIL_USER_NAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_FROM=os.getenv('MAIL_FROM'),
    MAIL_PORT=int(os.getenv('MAIL_PORT')),
    MAIL_SERVER=os.getenv('MAIL_SERVER'),
    MAIL_TLS=True,
    MAIL_SSL=False,

    TEMPLATE_FOLDER= Path(__file__).parent.parent/'templates/'
)




async def send_email_async(subject:str, email_to:EmailStr, body:dict,template:str):
 
    
    
    
    message = MessageSchema(
        subject=subject,
        recipients= [email_to,],
        template_body=body,
        
    )

    fm = FastMail(config)
    try:
        await fm.send_message(message, template_name=template)
        return True
    except ConnectionErrors as e:
        # print(e)
        return False