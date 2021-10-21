from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from forms import ContactForm, PersonaForm, UploadPersonaImg
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)


# Initialize database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///career.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Configure tables
class Persona(db.Model):
    __tablename__ = "personalists"
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(250), nullable=True)
    area = db.Column(db.String(50), nullable=False)

db.create_all()


# Frontend routes
@app.route('/')
def home():
    persona_list = Persona.query.all()
    return render_template("./pages/index.html", persona_list=persona_list)


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


# Admin routes
@app.route('/admin/add-persona', methods=["GET", "POST"])
def add_persona():
    form = PersonaForm()
    if form.validate_on_submit():
        if Persona.query.filter_by(email=form.email.data).first():
            flash("Tento personalista již existuje v naší databázi!")
            return redirect(url_for("add_persona"))
        new_persona = Persona(
            fullname=form.fullname.data,
            position=form.position.data,
            phone=form.phone.data,
            email=form.email.data,
            area=form.area.data
        )
        db.session.add(new_persona)
        db.session.flush()
        db.session.commit()
        return redirect(url_for("upload_persona_img", pers_id=new_persona.id))
    return render_template("./admin/edit_persona.html", form=form)


@app.route('/admin/upload-persona-img/<int:pers_id>', methods=["GET", "POST"])
def upload_persona_img(pers_id):
    form = UploadPersonaImg()
    persona = Persona.query.get(pers_id)
    if form.validate_on_submit():
        img_name = secure_filename(form.image.data.filename)
        img_file = f"images/{img_name}"
        form.image.data.save(f"./static/{img_file}")
        persona.image_url = img_file.replace("./static/", "")
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("./admin/upload_image.html", form=form)
        

@app.route('/admin/edit-persona/<int:pers_id>', methods=["GET", "POST"])
def edit_persona(pers_id):
    persona = Persona.query.get(pers_id)
    edit_form = PersonaForm(obj=persona)
    if edit_form.validate_on_submit():
        persona.fullname = edit_form.fullname.data
        persona.position = edit_form.position.data
        persona.phone = edit_form.phone.data
        persona.email = edit_form.email.data
        persona.area = edit_form.area.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("./admin/edit_persona.html", form=edit_form)


@app.route('/admin/delete-persona/<int:pers_id>', methods=["GET", "POST"])
def delete_persona(pers_id):
    persona = Persona.query.get(pers_id)
    db.session.delete(persona)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port="5000", debug=True)
