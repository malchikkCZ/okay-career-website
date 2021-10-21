import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


# Contact form
class ContactForm(FlaskForm):
    name = StringField("Jméno", validators=[DataRequired()], render_kw={"placeholder": "Jméno"})
    surname = StringField("Příjmení", validators=[DataRequired()], render_kw={"placeholder": "Příjmení"})
    email = StringField("Email", validators=[DataRequired()], render_kw={"placeholder": "E-mail"})
    file = FileField("Životopis", validators=[FileRequired()])
    message = TextAreaField("Váš vzkaz", validators=[DataRequired()], render_kw={"placeholder": "Váš vzkaz", "rows": 8})
    submit = SubmitField("Odeslat")

    def send_email(self):
        name = self.name.data
        surname = self.surname.data
        email = self.email.data
        filename = secure_filename(self.file.data.filename)
        path = "./files/"
        if not os.path.exists(path):
            os.makedirs(path)
        self.file.data.save(f"{path}{filename}")
        message = self.message.data

        msg = MIMEMultipart()
        msg["From"] = email
        msg["To"] = "malchikk@live.com"
        msg["Subject"] = f"{surname} {name} má zájem o práci"
        msg.attach(MIMEText(f"Zpráva od:\n\n{surname} {name}\n{email}\n\n{message}", "plain"))

        payload = MIMEBase("application", "octate-stream")
        with open(f"{path}{filename}", "rb") as file:
            payload.set_payload(file.read())
            encoders.encode_base64(payload)
            payload.add_header('Content-Disposition', 'attachement', filename=filename)
            msg.attach(payload)
        text = msg.as_string()

        with smtplib.SMTP("smtp.gmail.com") as mailserver:
            mailserver.starttls()
            mailserver.login(user="testokay2021@gmail.com", password="ifAAyV2PiejBk9i")
            mailserver.sendmail(
                from_addr=email,
                to_addrs="malchikk@live.com",
                msg=text
            )
        os.remove(f"{path}{filename}")


# Add or edit persona form
class PersonaForm(FlaskForm):
    fullname = StringField("Jméno a příjmení", validators=[DataRequired()], render_kw={"placeholder": "Jméno a příjmení"})
    position = StringField("Pozice", validators=[DataRequired()], render_kw={"placeholder": "Pozice"})
    phone = StringField("Tel. číslo", validators=[DataRequired()], render_kw={"placeholder": "Tel. číslo"})
    email = StringField("Email", validators=[DataRequired()], render_kw={"placeholder": "E-mail"})
    area = StringField("Oblast působnosti", validators=[DataRequired()], render_kw={"placeholder": "Oblast působnosti"})
    submit = SubmitField("Uložit")

class UploadPersonaImg(FlaskForm):
    image = FileField("Fotografie", validators=[FileRequired()])
    submit = SubmitField("Uložit")
