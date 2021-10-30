from webApp import db
from flask_login import UserMixin


class Setting(db.Model):
    __tablename__ = "settings"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.String(250), nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean(100), nullable=False)


class Section(db.Model):
    __tablename__ = "sections"
    id = db.Column(db.Integer, primary_key=True)
    title_cs = db.Column(db.String(100), nullable=False)
    title_sk = db.Column(db.String(100), nullable=False)
    body_cs = db.Column(db.Text, nullable=False)
    body_sk = db.Column(db.Text, nullable=False)
    context = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(250), nullable=True)


class Persona(db.Model):
    __tablename__ = "personalists"
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    position_cs = db.Column(db.String(100), nullable=False)
    position_sk = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(250), nullable=True)
    area = db.Column(db.String(50), nullable=False)


class Video(db.Model):
    __tablename__ = "videos"
    id = db.Column(db.Integer, primary_key=True)
    video_url = db.Column(db.String(100), nullable=False)
    video_context = db.Column(db.String(100), nullable=False)


class Candidate(db.Model):
    __tablename__ = "candidates"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(100), nullable=False)
    fullname = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    file = db.Column(db.String(250), nullable=False)
    message = db.Column(db.Text, nullable=False)