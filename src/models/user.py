from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    full_name = Column(String)
    total_questions_answered = Column(Integer)

    question_answers = relationship("QuestionAnswer", back_populates="user")


class QuestionAnswer(Base):
    __tablename__ = 'question_answers'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    question_id = Column(String)
    question_var = Column(String)
    answer = Column(String)

    user = relationship("User", back_populates="question_answers")
