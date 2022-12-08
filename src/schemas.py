# Untuk schemas.py

from pydantic import BaseModel

'''
Schemas
'''
class User(BaseModel):
	username:str
	password:str
	email:str

class UserView(BaseModel):
	username: str
	email:str

	class Config:
		orm_mode = True

