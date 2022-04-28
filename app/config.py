
from pydantic import BaseSettings



class Settings(BaseSettings):
    project_name :str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    database_username:str
    database_password:str
    database_hostname:str
    database_name:str
    database_port:str
    frontend_url:str
    



    class Config():
        env_file = '.env'



settings = Settings()

