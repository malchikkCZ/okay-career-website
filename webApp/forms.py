from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import (BooleanField, PasswordField, SelectField, StringField,
                     SubmitField, TextAreaField)
from wtforms.validators import URL, DataRequired, EqualTo


# Contact form
class ContactForm(FlaskForm):
    name = StringField("Jméno", validators=[DataRequired()])
    surname = StringField("Příjmení", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    file = FileField("Životopis", validators=[FileRequired()])
    message = TextAreaField("Váš vzkaz", validators=[
                            DataRequired()], render_kw={"rows": 8})
    terms = BooleanField("Souhlas", validators=[DataRequired()])
    submit = SubmitField("Odeslat")


# Administrator forms
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Heslo", validators=[DataRequired()])
    submit = SubmitField("Přihlásit")


class PasswordForm(FlaskForm):
    old_password = PasswordField("Staré heslo", validators=[DataRequired()])
    new_password = PasswordField("Nové heslo", validators=[DataRequired()])
    new_again = PasswordField("Nové heslo pro kontrolu", validators=[EqualTo('new_password'), DataRequired()])
    submit = SubmitField("Změnit heslo")


class UserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    name = StringField("Uživatelské jméno", validators=[DataRequired()])
    submit = SubmitField("Uložit")


class SetEmail(FlaskForm):
    value = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Uložit")


class SetJson(FlaskForm):
    json = TextAreaField("Jazykový JSON", validators=[DataRequired()], render_kw={"rows": 20})
    submit = SubmitField("Uložit")


# Add page section form
class SectionForm(FlaskForm):
    title_cs = StringField("Český titulek", validators=[DataRequired()])
    title_sk = StringField("Slovenský titulek", validators=[DataRequired()])
    body_cs = CKEditorField("Český text", validators=[DataRequired()])
    body_sk = CKEditorField("Slovenský text", validators=[DataRequired()])
    submit = SubmitField("Uložit")


class UploadSectionImg(FlaskForm):
    image = FileField(
        "Obrázek", 
        validators=[
            FileRequired(), 
            FileAllowed(['jpg', 'png', 'JPG', 'PNG'], 'Pouze JPG a PNG obrázky!')
            ]
        )
    submit = SubmitField("Uložit")


class VideoForm(FlaskForm):
    video_url = StringField("Adresa odkazu na YouTube", validators=[DataRequired(), URL()])
    submit = SubmitField("Uložit")


# Add persona form
class PersonaForm(FlaskForm):
    fullname = StringField("Jméno a příjmení", validators=[DataRequired()])
    position_cs = StringField("Název pozice (česky)", validators=[DataRequired()])
    position_sk = StringField(
        "Název pozice (slovensky)", validators=[DataRequired()])
    phone = StringField("Tel. číslo", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    area = SelectField(
        "Oblast působnosti", 
        choices=["centrala", "prodejny", "sklady"], 
        validators=[DataRequired()]
        )
    submit = SubmitField("Uložit")


class UploadPersonaImg(FlaskForm):
    image = FileField(
        "Fotografie", 
        validators=[
            FileRequired(), 
            FileAllowed(['jpg', 'png', 'JPG', 'PNG'], 'Pouze JPG a PNG obrázky!')
            ]
        )
    submit = SubmitField("Uložit")
