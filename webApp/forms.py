from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm, RecaptchaField, Recaptcha
from flask_wtf.file import FileAllowed, FileField, FileRequired, FileSize
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import URL, DataRequired, EqualTo, Email


### Contact form for candidates

class ContactForm(FlaskForm):
    name = StringField("Jméno", validators=[DataRequired()])
    surname = StringField("Příjmení", validators=[DataRequired()])
    email = StringField("Email", validators=[Email(), DataRequired()])
    file = FileField("Životopis", validators=[FileRequired(), FileSize(max_size=5242880, message="Příloha formuláře níže musí být menší než 5 MB.")])
    message = TextAreaField("Váš vzkaz", validators=[DataRequired()], render_kw={"rows": 8})
    recaptcha = RecaptchaField(validators=[Recaptcha(message="Prosím potvrďte ve formuláři níže, že nejste robot.")])
    terms = BooleanField("Souhlas", validators=[DataRequired()])
    submit = SubmitField("Odeslat")


### Administrator forms

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[Email(), DataRequired()])
    password = PasswordField("Heslo", validators=[DataRequired()])
    submit = SubmitField("Přihlásit")


class PasswordForm(FlaskForm):
    old_password = PasswordField("Staré heslo", validators=[DataRequired()])
    new_password = PasswordField("Nové heslo", validators=[DataRequired()])
    new_again = PasswordField("Nové heslo pro kontrolu", validators=[EqualTo('new_password'), DataRequired()])
    submit = SubmitField("Změnit heslo")


class UserForm(FlaskForm):
    email = StringField("Email", validators=[Email(), DataRequired()])
    name = StringField("Uživatelské jméno", validators=[DataRequired()])
    submit = SubmitField("Uložit")


class SetEmail(FlaskForm):
    value = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Uložit")


class SetJson(FlaskForm):
    json = TextAreaField("Jazykový JSON", validators=[DataRequired()], render_kw={"rows": 20})
    submit = SubmitField("Uložit")


### Forms to manage frontend content
 
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
            FileAllowed(['jpg', 'png', 'JPG', 'PNG'], 'Používejte pouze JPG a PNG obrázky!'),
            FileSize(max_size=5242880, message="Použitý obrázek je příliš velký pro zobrazení na webu. Maximální velikost je 5 MB.")
            ]
        )
    submit = SubmitField("Uložit")


class VideoForm(FlaskForm):
    video_url = StringField("Adresa odkazu na YouTube", validators=[DataRequired(), URL()])
    submit = SubmitField("Uložit")


### Forms to manage personalists

class PersonaForm(FlaskForm):
    fullname = StringField("Jméno a příjmení", validators=[DataRequired()])
    position_cs = StringField("Název pozice (česky)", validators=[DataRequired()])
    position_sk = StringField(
        "Název pozice (slovensky)", validators=[DataRequired()])
    phone = StringField("Tel. číslo", validators=[DataRequired()])
    email = StringField("Email", validators=[Email(), DataRequired()])
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
            FileAllowed(['jpg', 'png', 'JPG', 'PNG'], 'Používejte pouze JPG a PNG obrázky!'),
            FileSize(max_size=5242880, message="Použitý obrázek je příliš velký pro zobrazení na webu. Maximální velikost je 5 MB.")
            ]
        )
    submit = SubmitField("Uložit")
