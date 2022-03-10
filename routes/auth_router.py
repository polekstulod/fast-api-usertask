from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from database import get_db
from models.user_model import User
from schemas.auth_schema import TokenData, AuthForm
from schemas.user_schema import CreateUser
from jose import jwt
from passlib.context import CryptContext

# using: openssl rand -hex 32
AUTH_SECRET = '07774dad34fe4a073e7e978751fba97632bea34dc004328f8306249c0128e42e'
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def password_verify(plain, hashed):
    return pwd_context.verify(plain, hashed)


def password_hash(password):
    return pwd_context.hash(password)


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post('/signup')
def signup(request: CreateUser, db: Session = Depends(get_db)):
    try:
        print(request.email, request.password)
        request.password = password_hash(request.password)
        user = User(
            email=request.email,
            password=request.password
        )
        db.add(user)
        db.commit()
        return {'message': 'Sign Up Successful!'}
    except Exception as e:
        print(e)


@router.post('/login')
def login(form: AuthForm, response: Response, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == form.email,User.status ==1).first()
        if user:
            match = password_verify(form.password, user.password)
            if match:
                data = TokenData(author_id=user.user_id,
                                 email=user.email)
                token = jwt.encode(dict(data), AUTH_SECRET)
                response.set_cookie('token', token, httponly=True)
                return {'message': 'Login Success!'}

        return {'message': 'User not found. Please Sign Up first.'}
    except Exception as e:
        print(e)


@router.post('/logout')
def logout(response: Response):
    response.delete_cookie('token')
    return {'message': 'Logout Success!'}
