from email.mime.text import MIMEText
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
import smtplib


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)


class ContactForm(FlaskForm):
    name = StringField("Jméno", validators=[DataRequired()], render_kw={"placeholder": "Jméno"})
    surname = StringField("Příjmení", validators=[DataRequired()], render_kw={"placeholder": "Příjmení"})
    email = StringField("Email", validators=[DataRequired()], render_kw={"placeholder": "E-mail"})
    message = TextAreaField("Váš vzkaz", validators=[DataRequired()], render_kw={"placeholder": "Váš vzkaz", "rows": 8})
    submit = SubmitField("Odeslat")


def send_email(form):
    name = form.name.data
    surname = form.surname.data
    email = form.email.data
    message = form.message.data

    msg = f"Subject:{surname} {name} má zájem o práci\n\n{surname} {name} napsal:\n\n{message}"
    with smtplib.SMTP("smtp.gmail.com") as mailserver:
        mailserver.starttls()
        mailserver.login(user="testokay2021@gmail.com", password="ifAAyV2PiejBk9i")
        mailserver.sendmail(
            from_addr=email,
            to_addrs="malchikk@live.com",
            msg=msg.encode("utf8")
        )


@app.route('/')
def home():
    return render_template("./pages/index.html")


@app.route('/dekujeme')
def message_sent():
    return render_template("./pages/thankyou.html")


@app.route('/centrala', methods=["GET", "POST"])
def hq():
    form = ContactForm()
    if form.validate_on_submit():
        send_email(form)
        return redirect(url_for('message_sent'))
    return render_template("./pages/hq.html", form=form, context="hq")


@app.route('/prodejny', methods=["GET", "POST"])
def stores():
    form = ContactForm()
    if form.validate_on_submit():
        send_email(form)
        return redirect(url_for('message_sent'))
    return render_template("./pages/stores.html", form=form, context="stores")


@app.route('/sklady', methods=["GET", "POST"])
def warehouses():
    form = ContactForm()
    if form.validate_on_submit():
        send_email(form)
        return redirect(url_for('message_sent'))
    return render_template("./pages/warehouses.html", form=form, context="warehouses")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port="5000", debug=True)
