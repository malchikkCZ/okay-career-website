import os
from flask import Flask, render_template, redirect, url_for, flash, abort, request, json
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from forms import ContactForm, LoginForm, PasswordForm, UserForm, SectionForm, UploadSectionImg, PersonaForm, UploadPersonaImg, VideoForm
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
ckeditor = CKEditor(app)
Bootstrap(app)


# Initialize database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///career.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///career'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

def set_language():
    lang = str(request.accept_languages)
    basedir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(basedir, "static/lang.json"), encoding="utf-8") as json_data:
        data = json.load(json_data)
    if "sk" in lang.lower():
        return "sk", data
    else:
        return "cs", data


# Configure tables
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

db.create_all()


# Frontend routes
@app.route('/')
def index():
    lang, locale = set_language()
    sections = Section.query.filter_by(context="index")
    persona_list = Persona.query.all()
    return render_template("pages/index.html", lang=lang, loc=locale, sections=sections, persona_list=persona_list)


@app.route('/centrala', methods=["GET", "POST"])
def centrala():
    is_sent = False
    lang, locale = set_language()
    form = ContactForm()
    sections = Section.query.filter_by(context="centrala")
    video = Video.query.filter_by(video_context="centrala").first()
    if form.validate_on_submit():
        form.send_email()
        is_sent = True
    return render_template("pages/mainpage.html", lang=lang, loc=locale, sections=sections, video=video, form=form, success=is_sent, context="centrala")


@app.route('/prodejny', methods=["GET", "POST"])
def prodejny():
    is_sent = False
    lang, locale = set_language()
    form = ContactForm()
    sections = Section.query.filter_by(context="prodejny")
    video = Video.query.filter_by(video_context="prodejny").first()
    if form.validate_on_submit():
        form.send_email()
        is_sent = True
    return render_template("pages/mainpage.html", lang=lang, loc=locale, sections=sections, video=video, form=form, success=is_sent, context="prodejny")


@app.route('/sklady', methods=["GET", "POST"])
def sklady():
    is_sent = False
    lang, locale = set_language()
    form = ContactForm()
    sections = Section.query.filter_by(context="sklady")
    video = Video.query.filter_by(video_context="sklady").first()
    if form.validate_on_submit():
        form.send_email()
        is_sent = True
    return render_template("pages/mainpage.html", lang=lang, loc=locale, sections=sections, video=video, form=form, success=is_sent, context="sklady")


# Admin routes
@app.route('/admin', methods=["GET", "POST"])
def login():
    form = LoginForm()
    form_title = "Přihlášení"
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user or user.active == False:
            flash("Tento administrátor neexistuje nebo byl zrušen!")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            flash("Zadali jste špatné heslo, zkuste to prosím znovu!")
            return redirect(url_for("login")) 
        else:
            login_user(user)
            return redirect(url_for("index"))
    return render_template("admin/form.html", form=form, title=form_title)


@app.route('/logout')
@admin_only
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/admin/update/<int:user_id>', methods=["GET", "POST"])
@admin_only
def password(user_id):
    form = PasswordForm()
    user = User.query.get(user_id)
    if not user:
        flash("Nejprve se musíte přihlásit!")
        return redirect(url_for('login'))
    form_title = f"Změnit heslo pro uživatele {user.name}"
    if form.validate_on_submit():
        old_password = form.old_password.data
        if not check_password_hash(user.password, old_password):
            flash("Původní heslo nesouhlasí, zkuste to prosím znovu!")
            return redirect(url_for('password', user_id=user_id))
        if form.new_password.data != form.new_again.data:
            flash("Nová hesla nejsou stejná, zkuste to prosím znovu!")
            return redirect(url_for('password', user_id=user_id))
        hashed_password = generate_password_hash(form.new_password.data, method="pbkdf2:sha256", salt_length=8)
        user.password = hashed_password
        db.session.commit()
        return redirect(url_for('index'))
    return render_template("admin/form.html", form=form, title=form_title)


@app.route('/admin/add-user', methods=["GET", "POST"])
@admin_only
def register():
    form = UserForm()
    form_title = "Přidej uživatele"
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Tento administrátor již existuje v naší databázi!")
            return redirect(url_for("register"))
        hashed_password = generate_password_hash(form.password.data, method="pbkdf2:sha256", salt_length=8)
        new_user = User(
            email=form.email.data,
            password=hashed_password,
            name=form.name.data,
            active=True
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("admin/form.html", form=form, title=form_title)


@app.route('/admin/users')
@admin_only
def administrators():
    users_list = User.query.all()
    return render_template("admin/admins.html", users=users_list)


@app.route('/admin/switch/<int:user_id>')
@admin_only
def switch(user_id):
    if user_id == 1:
        return redirect(url_for('administrators'))
    user = User.query.get(user_id)
    if user.active == False:
        user.active = True
    else:
        user.active = False
    db.session.commit()
    if user_id == current_user.id:
        return redirect(url_for('logout'))
    return redirect(url_for('administrators'))


@app.route('/admin/delete/<int:user_id>')
@admin_only
def del_user(user_id):
    if user_id == 1:
        return redirect(url_for('administrators'))
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    if user_id == current_user.id:
        return redirect(url_for('logout'))
    return redirect(url_for('administrators'))


# TODO: Admin route to send administrator a new password
# TODO: Admin route to see stored messages
# TODO: Admin route to set basic settings
# TODO: Admin route to add custom pages
# TODO: Admin route to customize top bar menu
# TODO: Admin route to customize social networks in footer


# Admin section routes
@app.route('/admin/add-section/<context>', methods=["GET", "POST"])
@admin_only
def add_section(context):
    form = SectionForm()
    form_title = f"Přidej nový odstavec na stránce: {context}"
    if form.validate_on_submit():
        new_section = Section(
            title_cs=form.title_cs.data,
            title_sk=form.title_sk.data,
            body_cs=form.body_cs.data,
            body_sk=form.body_sk.data,
            context=context
        )
        db.session.add(new_section)
        db.session.flush()
        db.session.commit()
        return redirect(url_for("upload_section_img", section_id=new_section.id))
    return render_template("admin/form.html", form=form, title=form_title)


@app.route('/admin/upload-section-image/<int:section_id>', methods=["GET", "POST"])
@admin_only
def upload_section_img(section_id):
    form = UploadSectionImg()
    section = Section.query.get(section_id)
    context = section.context
    form_title = f"Nahrej obrázek pro odstavec: {section.title_cs}"
    if form.validate_on_submit():
        img_name = secure_filename(form.image.data.filename)
        img_file = f"images/{img_name}"
        basedir = os.path.abspath(os.path.dirname(__file__))
        form.image.data.save(os.path.join(basedir, f"static/{img_file}"))
        section.image_url = img_file.replace("./static/", "")
        db.session.commit()
        return redirect(url_for(context))
    return render_template("admin/form.html", form=form, title=form_title)


@app.route('/admin/edit_section/<int:section_id>', methods=["GET", "POST"])
@admin_only
def edit_section(section_id):
    section = Section.query.get(section_id)
    context = section.context
    form = SectionForm(obj=section)
    form_title = f"Uprav odstavec {section.title_cs} na stránce {section.context}"
    if form.validate_on_submit():
        section.title_cs = form.title_cs.data
        section.title_sk = form.title_sk.data
        section.body_cs = form.body_cs.data
        section.body_sk = form.body_sk.data
        db.session.commit()
        return redirect(url_for(context))
    return render_template("admin/form.html", form=form, title=form_title)


@app.route('/admin/delete-section/<int:section_id>', methods=["GET", "POST"])
@admin_only
def delete_section(section_id):
    section = Section.query.get(section_id)
    context = section.context
    db.session.delete(section)
    db.session.commit()
    return redirect(url_for(context))


@app.route('/admin/add-video/<context>', methods=["GET", "POST"])
@admin_only
def add_video(context):
    video = Video.query.filter_by(video_context=context).first()
    if video:
        form = VideoForm(obj=video)
    else:
        form = VideoForm()
    form_title = f"Nahrej odkaz na video na stránku {context}"
    if form.validate_on_submit():
        if video:
            video.video_url = form.video_url.data
            db.session.commit()
        else:
            new_video = Video(
                video_url=form.video_url.data,
                video_context=context
            )            
            db.session.add(new_video)
            db.session.commit()
        return redirect(url_for(context))
    return render_template("admin/form.html", form=form, title=form_title)


@app.route('/admin/delete-video/<int:video_id>', methods=["GET", "POST"])
@admin_only
def delete_video(video_id):
    video = Video.query.get(video_id)
    context = video.video_context
    db.session.delete(video)
    db.session.commit()
    return redirect(url_for(context))


# Admin persona routes
@app.route('/admin/add-persona', methods=["GET", "POST"])
@admin_only
def add_persona():
    form = PersonaForm()
    form_title = "Přidej personalistu"
    if form.validate_on_submit():
        if Persona.query.filter_by(email=form.email.data).first():
            flash("Tento personalista již existuje v naší databázi!")
            return redirect(url_for("add_persona"))
        new_persona = Persona(
            fullname=form.fullname.data,
            position_cs=form.position_cs.data,
            position_sk=form.position_sk.data,
            phone=form.phone.data,
            email=form.email.data,
            area=form.area.data
        )
        db.session.add(new_persona)
        db.session.flush()
        db.session.commit()
        return redirect(url_for("upload_persona_img", pers_id=new_persona.id))
    return render_template("admin/form.html", form=form, title=form_title)


@app.route('/admin/upload-persona-image/<int:pers_id>', methods=["GET", "POST"])
@admin_only
def upload_persona_img(pers_id):
    form = UploadPersonaImg()
    persona = Persona.query.get(pers_id)
    form_title = f"Nahrej fotografii pro {persona.fullname}"
    if form.validate_on_submit():
        img_name = secure_filename(form.image.data.filename)
        img_file = f"images/{img_name}"
        basedir = os.path.abspath(os.path.dirname(__file__))
        form.image.data.save(os.path.join(basedir, f"static/{img_file}"))
        persona.image_url = img_file.replace("./static/", "")
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("admin/form.html", form=form, title=form_title)
        

@app.route('/admin/edit-persona/<int:pers_id>', methods=["GET", "POST"])
@admin_only
def edit_persona(pers_id):
    persona = Persona.query.get(pers_id)
    form = PersonaForm(obj=persona)
    form_title = f"Uprav detaily pro {persona.fullname}"
    if form.validate_on_submit():
        persona.fullname = form.fullname.data
        persona.position_cs = form.position_cs.data
        persona.position_sk = form.position_sk.data
        persona.phone = form.phone.data
        persona.email = form.email.data
        persona.area = form.area.data
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("admin/form.html", form=form, title=form_title)


@app.route('/admin/delete-persona/<int:pers_id>', methods=["GET", "POST"])
@admin_only
def delete_persona(pers_id):
    persona = Persona.query.get(pers_id)
    db.session.delete(persona)
    db.session.commit()
    return redirect(url_for("index"))


# TODO: Remove debug settings below
if __name__ == "__main__":
    app.run(host="127.0.0.1", port="5000", debug=True)
