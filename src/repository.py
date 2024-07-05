from context.db import SessionLocal
from models.user import User
from sqlalchemy.orm import Session


def get_user_by_email(email: str):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()
    return user

# get all users
def get_users():
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return users

def create_user(user: User):
    db = SessionLocal()
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

def update_user(user: User):
    db = SessionLocal()
    db.query(User).filter(User.id == user.id).update(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

def delete_user(user: User):
    db = SessionLocal()
    db.delete(user)
    db.commit()
    db.close()
    return user


# get current questions answered by user email
def get_user_questions_answered(email: str):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()
    return user.total_questions_answered

# update total questions answered by user email
def update_user_questions_answered(email: str, total_questions_answered: int):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    user.total_questions_answered = total_questions_answered
    db.commit()
    db.refresh(user)
    db.close()
    return user.total_questions_answered

