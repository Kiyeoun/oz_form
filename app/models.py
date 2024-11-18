# SQLAchemy 모델 정의
# 마시멜로로 스키마 생성
from datetime import datetime, timezone
from enum import Enum
from config import db


class AgeStatus(Enum):
    teen = "teen"
    twenty = "twenty"
    thirty = "thirty"
    fourty = "fourty"
    fifty = "fifty"


class GenderStatus(Enum):
    male = "male"
    female = "female"


class ImageStatus(Enum):
    main = "main"
    sub = "sub"


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Enum(AgeStatus), nullable=False)
    gender = db.Column(db.Enum(GenderStatus), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age.value if hasattr(self.age, "value") else self.age,
            "gender": (
                self.gender.value if hasattr(self.gender, "value") else self.gender
            )
        }


class Image(db.Model):
    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.TEXT, nullable=False)
    type = db.Column(db.Enum(ImageStatus), nullable=False)

    questions = db.relationship("Question", back_populates="image")

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "type": self.type.value if hasattr(self.type, "value") else self.type
            # enum을 한 번 더 확인하는 코드, self.type의 속성 중에 "value"가 있으면 True(기본적으로 enum은 value속성을 갖고 있다)
            # self.type.value => 예를 들어 속성이 main이면 ImageStatus.main.value = "main"이 된다. ImageStatus.main까지만 적혀있으면 그냥 enum객체 취급이다.
        }


class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    sqe = db.Column(db.Integer, nullable=False)

    image_id = db.Column(db.Integer, db.ForeignKey("images.id"), nullable=False)

    image = db.relationship("Image", back_populates="questions")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "is_active": self.is_active,
            "sqe": self.sqe,
            "image": self.image.to_dict() if self.image else None,
        }


class DetailQuestion(db.Model):
    __tablename__ = "detail_questions"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    sqe = db.Column(db.Integer, nullable=False)

    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "is_active": self.is_active,
            "sqe": self.sqe,
            "question_id": self.question_id,
        }


class Answer(db.Model):
    __tablename__ = "answers"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    detail_question_id = db.Column(db.Integer, db.ForeignKey("detail_questions.id"))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "detail_question_id": self.detail_question_id,
        }