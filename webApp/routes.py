import os
from datetime import datetime
from random import randint

from flask import flash, json, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from webApp import app, db
from webApp.forms import (ContactForm, LoginForm, PasswordForm, PersonaForm,
                          SectionForm, SetEmail, SetJson, UploadPersonaImg,
                          UploadSectionImg, UserForm, VideoForm)
from webApp.models import Candidate, Persona, Section, Setting, User, Video


def set_language():
    lang = request.accept_languages.best_match(['cs', 'sk'])
    if not lang:
        lang = "cs"
    basedir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(basedir, "static", "lang.json"), encoding="utf-8") as json_data:
        data = json.load(json_data)
    return lang, data


### Frontend routes

@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
    lang, locale = set_language()
    sections = Section.query.filter_by(context="index")
    persona_list = Persona.query.all()
    return render_template("index.html", lang=lang, loc=locale, sections=sections, persona_list=persona_list)


@app.route('/pages/<context>', methods=["GET", "POST"])
def mainpage(context):
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
        recipient = Setting.query.filter_by(name="email").first().value
        new_candidate.send_by_email(recipient, fullpath)
        db.session.add(new_candidate)
        db.session.commit()
        flash(locale["alerts"]["email_sent"][lang])
        return redirect(url_for('mainpage', context=context))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(err_msg[0], category='danger')
    return render_template("mainpage.html", lang=lang, loc=locale, sections=sections, video=video, form=form, context=context)


### Admin routes for administrators

@app.route('/admin', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash(f"Jste přihlášen(a) jako: {current_user.name}")
        return redirect(url_for("index"))
    form = LoginForm()
    form_title = "Přihlášení"
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user or user.active == False:
            flash("Tento administrátor neexistuje nebo byl zrušen!", category="danger")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            flash("Zadali jste špatné heslo, zkuste to prosím znovu!", category="danger")
            return redirect(url_for("login"))
        else:
            login_user(user)
            flash(f"Jste přihlášen(a) jako: {user.name}")
            return redirect(url_for("index"))
    return render_template("admin/form.html", form=form, title=form_title)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(f"Byl(a) jste úspěšně odhlášen(a).")
    return redirect(url_for('index'))


@app.route('/admin/update/<int:user_id>', methods=["GET", "POST"])
@login_required
def password(user_id):
    form = PasswordForm()
    user = User.query.get(user_id)
    if not user:
        flash("Něco se pokazilo, nejprve se zkuste přihlásit.", category="info")
        return redirect(url_for('login'))
    form_title = f"Změnit heslo pro uživatele {user.name}"
    if form.validate_on_submit():
        old_password = form.old_password.data
        if not check_password_hash(user.password, old_password):
            flash("Původní heslo nesouhlasí, zkuste to prosím znovu!", category="danger")
            return redirect(url_for('password', user_id=user_id))
        hashed_password = generate_password_hash(
            form.new_password.data, method="pbkdf2:sha256", salt_length=8)
        user.password = hashed_password
        db.session.commit()
        flash("Vaše heslo bylo úspěšně změněno.")
        return redirect(url_for('index'))
    return render_template("admin/form.html", form=form, title=form_title)


@app.route('/admin/users')
@login_required
def administrators():
    users_list = User.query.all()
    return render_template("admin/admins.html", users=users_list)


@app.route('/admin/add-user', methods=["GET", "POST"])
@login_required
def register():
    form = UserForm()
    form_title = "Přidej uživatele"
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Tento administrátor již existuje v naší databázi!", category="info")
            return redirect(url_for("register"))
        new_user = User(
            email=form.email.data,
            password=User.generate_password(form.email.data),
            name=form.name.data,
            active=True
        )
        db.session.add(new_user)
        db.session.commit()
        flash(f"Nový uživatel byl úspěšně vytvořen, přihlašovací údaje byly zaslány na email: {new_user.email}", category="success")
        return redirect(url_for("index"))
    return render_template("admin/form.html", form=form, title=form_title)


@app.route('/admin/send_passwrd/<int:user_id>')
@login_required
def send_passwrd(user_id):
    user = User.query.get(user_id)
    user.password = user.generate_password(user.email)
    db.session.commit()
    flash(f"Přihlašovací údaje s novým heslem byly zaslány na email: {user.email}", category="success")
    return redirect(url_for('administrators'))


@app.route('/admin/switch/<int:user_id>')
@login_required
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
    flash(f"Status uživatele {user.name} byl úspěšně změněn.", category="success")
    return redirect(url_for('administrators'))


@app.route('/admin/delete/<int:user_id>')
@login_required
def del_user(user_id):
    if user_id == 1:
        flash("Superadmin účet není možné smazat.", category="info")
        return redirect(url_for('administrators'))
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    if user_id == current_user.id:
        return redirect(url_for('logout'))
    flash(f"Uživatel {user.name} byl nenávratně odstraněn z databáze.", category="success")
    return redirect(url_for('administrators'))


### Admin routes to set basic settings

@app.route('/admin/settings')
@login_required
def settings():
    return render_template("admin/settings.html")


@app.route('/admin/set-email', methods=["GET", "POST"])
@login_required
def set_email():
    form_title = "Nastavení primární adresy pro zasílání pošty"
    setting = Setting.query.filter_by(name="email").first()
    form = SetEmail(obj=setting)
    if form.validate_on_submit():
        setting.value = form.value.data
        db.session.commit()
        flash(f"Primární email pro zasílání pošty byl změněn na {form.value.data}.", category="success")
        return redirect(url_for('settings'))
    return render_template("admin/form.html", form=form, title=form_title)


@app.route('/admin/set-json', methods=["GET", "POST"])
@login_required
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
        flash("Jazykový JSON byl úspěšně uložen.", category="success")
        return redirect(url_for("settings"))
    form.json.data = lang_data
    return render_template("admin/form.html", form=form, title=form_title)


### Admin routes for candidates

@app.route('/admin/candidates', methods=["GET", "POST"])
@login_required
def candidates():
    candidates_list = Candidate.query.all()
    return render_template("admin/candidates.html", candidates=candidates_list)


@app.route('/admin/del-candidate/<int:candidate_id>', methods=["GET", "POST"])
@login_required
def del_candidate(candidate_id):
    candidate = Candidate.query.get(candidate_id)
    name = candidate.fullname
    basedir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(basedir, "files")
    os.remove(os.path.join(path, candidate.file))
    db.session.delete(candidate)
    db.session.commit()
    flash(f"Uchazeč {name} byl odstraněn z databáze.", category="success")
    return redirect(url_for('candidates'))


@app.route('/admin/download/<int:candidate_id>', methods=["GET", "POST"])
@login_required
def download(candidate_id):
    candidate = Candidate.query.get(candidate_id)
    basedir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(basedir, "files")
    return send_file(os.path.join(path, candidate.file), as_attachment=True)


### Admin routes for frontend sections

@app.route('/admin/add-section/<context>', methods=["GET", "POST"])
@login_required
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
@login_required
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
@login_required
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
@login_required
def delete_section(section_id):
    section = Section.query.get(section_id)
    context = section.context
    db.session.delete(section)
    db.session.commit()
    return redirect(url_for("mainpage", context=context))


@app.route('/admin/add-video/<context>', methods=["GET", "POST"])
@login_required
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
@login_required
def delete_video(video_id):
    video = Video.query.get(video_id)
    context = video.video_context
    db.session.delete(video)
    db.session.commit()
    return redirect(url_for("mainpage", context=context))


### Admin routes for personalists

@app.route('/admin/add-persona', methods=["GET", "POST"])
@login_required
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
@login_required
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
@login_required
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
@login_required
def delete_persona(pers_id):
    persona = Persona.query.get(pers_id)
    db.session.delete(persona)
    db.session.commit()
    return redirect(url_for("index"))
