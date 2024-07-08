from context.db import SessionLocal
from models.user import User, QuestionAnswer
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

def create_user(email: str, full_name: str):
    db = SessionLocal()
    user = User(email=email, full_name=full_name, total_questions_answered=0)
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
    if user is None:
        return 0
    return user.total_questions_answered

# update total questions answered by user email
def update_user_questions_answered(email: str, val: int):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    user.total_questions_answered = user.total_questions_answered + val
    db.commit()
    db.refresh(user)
    db.close()
    return user.total_questions_answered


# add answer to a question

def add_answer(email: str, question_id: str, question_var: str, answer: str):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        return None
    question_answer = QuestionAnswer(user_id=user.id, question_id=question_id, question_var=question_var, answer=answer)
    db.add(question_answer)
    db.commit()
    db.refresh(question_answer)
    db.close()
    return question_answer