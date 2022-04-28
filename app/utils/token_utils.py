from itsdangerous import URLSafeTimedSerializer, BadTimeSignature,SignatureExpired
from app.config import settings
from pydantic import EmailStr

token_algo= URLSafeTimedSerializer(settings.secret_key,salt='Email_Verification_&_Forgot_password')

def token(email: EmailStr):
    _token = token_algo.dumps(email)
    return _token

def verify_token(token:str):

    try:
        email = token_algo.loads(token, max_age=1800)
    except SignatureExpired:
        return None
    except BadTimeSignature:
        return None
    return {'email':email, 'check':True}



