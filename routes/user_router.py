from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from schemas.user_schema import CreateUser, UserDelete
from models.user_model import User
from database import get_db
from dependencies import get_token
from passlib.context import CryptContext

# using: openssl rand -hex 32
AUTH_SECRET = '07774dad34fe4a073e7e978751fba97632bea34dc004328f8306249c0128e42e'
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def password_verify(plain, hashed):
    return pwd_context.verify(plain, hashed)


def password_hash(password):
    return pwd_context.hash(password)


router = APIRouter(
    prefix='/users',
    tags=['users'],
    dependencies=[Depends(get_token)]
)


@router.get('/')
def all(db: Session = Depends(get_db), current_user: User = Depends(get_token)):

    print(current_user)
    users = db.query(User).filter(
        User.status == 1).all()
    # # returns list of all users [{...}, {...}, {...}] <- list comprehension?
    return {'users': [
        {
            'user_id': user.user_id,
            'email': user.email,
            'created_at': user.created_at,
            'updated_at': user.updated_at
        }
        for user in users
    ]
    }


@router.get('/current')
def find_by_id(current_user: User = Depends(get_token), db: Session = Depends(get_db)):

    user = db.query(User).filter(
        User.user_id == current_user['author_id']).first()
    if not user:
        raise HTTPException(404, 'User not found')
    return {
        'user': {
            'user_id': user.user_id,
            'email': user.email,
            'created_at': user.created_at,
            'updated_at': user.updated_at
        }
    }


@router.put('/update')
def update(user: CreateUser, db: Session = Depends(get_db), current_user: User = Depends(get_token)):
    user.password = password_hash(user.password)
    if not db.query(User).filter(User.user_id == current_user['author_id']).update({
        'email': user.email,
        'password': user.password
    }):
        raise HTTPException(404, 'User not found. Failed to update.')

    db.commit()
    return {'message': 'User updated successfully.'}


@router.delete('/{id}')
def remove(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_token)):

    if not db.query(User).filter(User.user_id == id, current_user['author_id'] != User.user_id).delete():
        raise HTTPException(
            404, 'User not found or you are deleting yourself. Deletion failed.')
    db.commit()
    return {'message': 'User removed successfully.'}



@router.put('/delete')
def softdel(user: UserDelete, db: Session = Depends(get_db), current_user: User = Depends(get_token)):

    if not db.query(User).filter(User.user_id == user.user_id, current_user['author_id'] != User.user_id).update({
        'status':user.status
    }):
        raise HTTPException(404, 'User not found. Failed to delete.')
    db.commit()
    return {'message': 'User removed successfully.'}