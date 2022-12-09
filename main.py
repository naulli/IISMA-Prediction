import jwt
import joblib
import pandas as pd
import numpy as np

from os import stat
from fastapi import FastAPI, Depends, HTTPException, APIRouter, Response, status
from fastapi import responses
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from tortoise import fields 
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model 
from pydantic import BaseModel
from jose import JWTError, jwt
from requests import request
import uvicorn

app = FastAPI(title="IISMA Application Prediction API",
    description="Layanan kalkulasi prediksi kemungkinan mahasiswa diterima dalam program IISMA berdasarkan input nilai, skor TOEFL, ranking universitas, nilai Statement of Purpose (Essay), nilai Letter of Reccomendation (Surat Rekomendasi), nilai Indeks Prestasi Kumulatif (CGPA), dan jumlah sertifikat. Masukkan nilai rentang 1-100 (score), 1-120 (TOEFL), 1-10 (university), 1-5 (SoP & LoR), 0-4 (CGPA), dan angka sesuai jumlah sertifikat yang dimiliki.")

JWT_SECRET = 'myjwtsecret'

# Auth Class
class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(50, unique=True)
    password_hash = fields.CharField(128)
    

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)


User_Pydantic = pydantic_model_creator(User, name='User')
UserIn_Pydantic = pydantic_model_creator(User, name='UserIn', exclude_readonly=True)


# Service Class
class GradRequest(BaseModel):
    name: str
    score: int
    toefl: int
    university: int
    sop: float
    lor: float
    cgpa: float
    certificate: int

# gradPydantic = pydantic_model_creator(GradRequest)

grad = joblib.load("models/grad.joblib")
sc = joblib.load("models/sc.bin")

class request_body(BaseModel):
    link: str

# Routes
# router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

async def authenticate_user(username: str, password: str):
    user = await User.get(username=username)
    if not user:
        return False 
    if not user.verify_password(password):
        return False
    return user 

users = []


@app.get('/', tags=["Root"])
async def root():
    print(users)
    return {"18220007 - Joanna Margareth Nauli" : "Selamat datang di laman rekomendasi untuk konsiderasi pendaftaran IISMA!"}


@app.post('/users', response_model=User_Pydantic, tags=["User"])
async def create_user(user: UserIn_Pydantic):
    user_obj = User(username=user.username, password_hash=bcrypt.hash(user.password_hash))
    await user_obj.save()
    return await User_Pydantic.from_tortoise_orm(user_obj)

# async def pred(music: gradPydantic, token: str = Depends(oauth2_scheme)):
#     payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
#     user = await User.get(id=payload.get('id'))
#     if user:
#         grad_obj = GradRequest(name=grad.name, gre=grad.gre, toefl=grad.toefl, university=grad.university, sop=grad.sop, lor=grad.lor, cgpa=grad.cgpa, research=grad.research)
#     return await gradPydantic.from_tortoise_orm(grad_obj)


@app.post('/token', tags=["User"])
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

    user_obj = await User_Pydantic.from_tortoise_orm(user)

    token = jwt.encode(user_obj.dict(), JWT_SECRET)

    return {'access_token' : token, 'token_type' : 'bearer'}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

    return await User_Pydantic.from_tortoise_orm(user)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="User belum terautentikasi!",
        )

@app.post('/iisma/', tags=["Core"])
async def IISMA_prediction(req: GradRequest, response: Response, token:str):
    user = verify_token(token)
    if(req.score < 0 or req.toefl < 0 or req.university < 0 or req.sop < 0 or req.lor < 0 or req.cgpa < 0 or req.certificate < 0):
        response.status_code = 400
        return {"message": "Fields cannot be less then 0"}
    df = np.array([req.score, req.toefl, 6 - req.university,
                   req.sop, req.lor, req.cgpa, req.certificate])

    new_df = sc.transform(df.reshape(1, -1))
    prediction = grad.predict(new_df)
    if(prediction[0] > 100):
        prediction[0] = 0.992
        # pred = "Selamat! Anda diterima di program IISMA"
        # return {"message": "Selamat! Anda diterima di program IISMA"}
    elif(prediction[0] < 0):
        prediction[0] = 0.0008
        # pred = "Maaf, Anda belum berhasil mengikuti program IISMA. Coba lagi tahun depan!"
        # return {"message": "Maaf, Anda belum berhasil mengikuti program IISMA. Coba lagi tahun depan!"}
    return {"name": req.name, "pred": "Kemungkinanmu diterima dalam program IISMA adalah sebesar {}".format(prediction[0])}

@app.post('/callPredict', tags=["News Validator"])
def Predict(link: request_body):
    url = "https://newsclassifiertst.azurewebsites.net/login"
    user = {
        "username": "johndoe",
        "password": "secret"
    }
    response = request("POST", url, data=user)
    print(response.json())
    access_token = response.json()["access token"]
    url = "https://newsclassifiertst.azurewebsites.net/predict"
    response2 = request("POST", url+'/?token='+access_token, data=link.json())
    return response2.json()

# @app.get('/users/me', response_model=User_Pydantic)
# async def get_user(user: User_Pydantic = Depends(get_current_user)):
#     return user    

# register_tortoise(
#     app, 
#     db_url='sqlite://db.sqlite3',
#     modules={'models': ['main']},
#     generate_schemas=True,
#     add_exception_handlers=True
# )

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8080)