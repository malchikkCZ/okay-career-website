import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)


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
        self.file.data.save('./temp/' + filename)
        message = self.message.data

        msg = MIMEMultipart()
        msg["From"] = email
        msg["To"] = "malchikk@live.com"
        msg["Subject"] = f"{surname} {name} má zájem o práci"
        msg.attach(MIMEText(f"{surname} {name} napsal:\n\n{message}", "plain"))

        payload = MIMEBase("application", "octate-stream")
        with open(f"./temp/{filename}", "rb") as file:
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
        os.remove("./temp/" + filename)


@app.route('/')
def home():
    return render_template("./pages/index.html")


@app.route('/centrala', methods=["GET", "POST"])
def hq():
    is_sent = False
    form = ContactForm()
    if form.validate_on_submit():
        form.send_email()
        is_sent = True
    return render_template("./pages/hq.html", form=form, success=is_sent, context="hq")


@app.route('/prodejny', methods=["GET", "POST"])
def stores():
    is_sent = False
    form = ContactForm()
    if form.validate_on_submit():
        form.send_email()
        is_sent = True
    return render_template("./pages/stores.html", form=form, success=is_sent, context="stores")


@app.route('/sklady', methods=["GET", "POST"])
def warehouses():
    is_sent = False
    form = ContactForm()
    if form.validate_on_submit():
        form.send_email()
        is_sent = True
    return render_template("./pages/warehouses.html", form=form, success=is_sent, context="warehouses")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port="5000", debug=True)
