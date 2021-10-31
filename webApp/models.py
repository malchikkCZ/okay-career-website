import os
import smtplib
import string

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask_login import UserMixin
from random import sample
from werkzeug.security import check_password_hash, generate_password_hash

from webApp import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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

    @staticmethod
    def generate_password(email):
        chars = string.ascii_letters + string.digits
        new_password = "".join(sample(chars, 8))

        msg = MIMEMultipart()
        msg["From"] = os.environ.get("SMTP_USER")
        msg["To"] = email
        msg["Subject"] = "Přihlašovací údaje pro OKAY Kariera"
        msg.attach(MIMEText(
            f"Uživatelské jméno: {email}\n" +
            f"Nové heslo do administrace: {new_password}\n\n" +
            f"Po přihlášení si jej prosím změňte.", "plain"))
        text_msg = msg.as_string()
    
        with smtplib.SMTP("smtp.gmail.com") as mailserver:
            mailserver.starttls()
            mailserver.login(user=os.environ.get("SMTP_USER"),
                            password=os.environ.get("SMTP_PASS"))
            mailserver.sendmail(
                from_addr=os.environ.get("SMTP_USER"),
                to_addrs=email,
                msg=text_msg
            )
        hashed_password = generate_password_hash(
            new_password, method="pbkdf2:sha256", salt_length=8)
        return hashed_password


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

    def send_by_email(self, recipient, path_to_file):
        msg = MIMEMultipart()
        msg["From"] = self.email
        msg["To"] = recipient
        msg["Subject"] = f"{self.fullname} má zájem o práci"
        msg.attach(
            MIMEText(f"Zpráva od:\n\n{self.fullname}\n{self.email}\n\n{self.message}", "plain"))

        payload = MIMEBase("application", "octate-stream")
        with open(path_to_file, "rb") as file:
            payload.set_payload(file.read())
            encoders.encode_base64(payload)
            payload.add_header('Content-Disposition',
                               'attachement', filename=self.file)
            msg.attach(payload)
        text = msg.as_string()

        with smtplib.SMTP("smtp.gmail.com") as mailserver:
            mailserver.starttls()
            mailserver.login(user=os.environ.get("SMTP_USER"),
                             password=os.environ.get("SMTP_PASS"))
            mailserver.sendmail(
                from_addr=self.email,
                to_addrs=recipient,
                msg=text
            )