import os
import smtplib
import string
from datetime import datetime
from functools import wraps
from random import randint, sample

from flask import (abort, flash, json, redirect, render_template, request,
                   send_file, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from webApp import app, db, login_manager
from webApp.forms import (ContactForm, LoginForm, PasswordForm, PersonaForm,
                          SectionForm, SetEmail, SetJson, UploadPersonaImg,
                          UploadSectionImg, UserForm, VideoForm)
from webApp.models import Candidate, Persona, Section, Setting, User, Video


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
    lang = request.accept_languages.best_match(['cs', 'sk'])
    if not lang:
        lang = "cs"
    basedir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(basedir, "static", "lang.json"), encoding="utf-8") as json_data:
        data = json.load(json_data)
    return lang, data


# Frontend routes
@app.route('/')
def index():
    lang, locale = set_language()
    sections = Section.query.filter_by(context="index")
    persona_list = Persona.query.all()
    return render_template("pages/index.html", lang=lang, loc=locale, sections=sections, persona_list=persona_list)


@app.route('/pages/<context>', methods=["GET", "POST"])
def mainpage(context):
    is_sent = False
    lang, locale = set_language()
    form = ContactForm()
    sections = Section.query.filter_by(context=context)
    video = Video.query.filter_by(video_context=context).first()
    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)

        basedir = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(basedir, "files")
        if not os.path.exists(path):
            os.makedirs(path)

        fullpath = os.path.join(path, filename)
        while os.path.isfile(fullpath):
            extension = filename[-4:]
            filename = filename[:-4] + str(randint(1000, 9999)) + extension
            fullpath = os.path.join(path, filename)
        form.file.data.save(fullpath)

        new_candidate = Candidate(
            timestamp=datetime.now().strftime("%d-%m-%Y %H:%M"),
            fullname=f"{form.surname.data} {form.name.data}",
            email=form.email.data,
            file=filename,
            message=form.message.data
        )
        db.session.add(new_candidate)
        db.session.commit()

        email = Setting.query.filter_by(name="email").first().value
        form.send_email(path, filename, email)
        is_sent = True
    return render_template("pages/mainpage.html", lang=lang, loc=locale, sections=sections, video=video, form=form, success=is_sent, context=context)


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
        hashed_password = generate_password_hash(
            form.new_password.data, method="pbkdf2:sha256", salt_length=8)
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
        hashed_password = generate_password_hash(
            form.password.data, method="pbkdf2:sha256", salt_length=8)
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


# Admin route to send administrator a new password
@app.route('/admin/send_passwrd/<int:user_id>')
@admin_only
def send_passwrd(user_id):
    user = User.query.get(user_id)
    chars = string.ascii_letters + string.digits
    new_passwrd = "".join(sample(chars, 8))
    while check_password_hash(user.password, new_passwrd):
        new_passwrd = "".join(sample(chars, 8))
    message = f"Subject:Nové heslo pro OKAY Kariera\n\nNové heslo do administrace: {new_passwrd}\nPo přihlášení si jej prosím změňte."
    with smtplib.SMTP("smtp.gmail.com") as mailserver:
        mailserver.starttls()
        mailserver.login(user=os.environ.get("SMTP_USER"),
                         password=os.environ.get("SMTP_PASS"))
        mailserver.sendmail(
            from_addr=os.environ.get("SMTP_USER"),
            to_addrs=user.email,
            msg=message.encode('utf8')
        )
    user.password = generate_password_hash(
        new_passwrd, method="pbkdf2:sha256", salt_length=8)
    db.session.commit()
    return redirect(url_for('administrators'))


# Admin route to set basic settings
@app.route('/admin/settings')
@admin_only
def settings():
    return render_template("admin/settings.html")


@app.route('/admin/set-email', methods=["GET", "POST"])
@admin_only
def set_email():
    form_title = "Nastavení primární adresy pro zasílání pošty"
    setting = Setting.query.filter_by(name="email").first()
    form = SetEmail(obj=setting)
    if form.validate_on_submit():
        setting.value = form.value.data
        db.session.commit()
        return redirect(url_for('settings'))
    return render_template("admin/form.html", form=form, title=form_title)


@app.route('/admin/set-json', methods=["GET", "POST"])
@admin_only
def set_json():
    basedir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(basedir, "static", "lang.json"), encoding="utf-8") as json_data:
        lang_data = json_data.read()
    form = SetJson()
    form_title = "Nastavení jazykového JSONu, buďte maximálně opatrní!"
    if form.validate_on_submit():
        new_json = form.json.data
        with open(os.path.join(basedir, "static", "lang.json"), "w", encoding="utf-8") as json_data:
            json_data.write(new_json)
        return redirect(url_for("settings"))
    form.json.data = lang_data
    return render_template("admin/form.html", form=form, title=form_title)


@app.route('/admin/candidates', methods=["GET", "POST"])
@admin_only
def candidates():
    candidates_list = Candidate.query.all()
    return render_template("admin/candidates.html", candidates=candidates_list)


@app.route('/admin/del-candidate/<int:candidate_id>', methods=["GET", "POST"])
@admin_only
def del_candidate(candidate_id):
    candidate = Candidate.query.get(candidate_id)
    basedir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(basedir, "files")
    os.remove(os.path.join(path, candidate.file))
    db.session.delete(candidate)
    db.session.commit()
    return redirect(url_for('candidates'))


@app.route('/admin/download/<int:candidate_id>', methods=["GET", "POST"])
@admin_only
def download(candidate_id):
    candidate = Candidate.query.get(candidate_id)
    basedir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(basedir, "files")
    return send_file(os.path.join(path, candidate.file), as_attachment=True)


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
        return redirect(url_for("mainpage", context=context))
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
        return redirect(url_for("mainpage", context=context))
    return render_template("admin/form.html", form=form, title=form_title)


@app.route('/admin/delete-section/<int:section_id>', methods=["GET", "POST"])
@admin_only
def delete_section(section_id):
    section = Section.query.get(section_id)
    context = section.context
    db.session.delete(section)
    db.session.commit()
    return redirect(url_for("mainpage", context=context))


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
        return redirect(url_for("mainpage", context=context))
    return render_template("admin/form.html", form=form, title=form_title)


@app.route('/admin/delete-video/<int:video_id>', methods=["GET", "POST"])
@admin_only
def delete_video(video_id):
    video = Video.query.get(video_id)
    context = video.video_context
    db.session.delete(video)
    db.session.commit()
    return redirect(url_for("mainpage", context=context))


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
