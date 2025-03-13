from flask import Flask
from flask import *
from flask_bootstrap import *
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
from flask_sqlalchemy import *
from flask_login import *
from utils import *
from flask_bcrypt import Bcrypt


app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = '55c02bd01e10ebbedf78e48c395e91451923c377'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

bootstrap = Bootstrap5(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
db = SQLAlchemy()
db.init_app(app)
bcrypt = Bcrypt(app)



class Schlüssel(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    nummer = db.Column(db.Integer, nullable=False)
    schluesselname = db.Column(db.String, nullable=False)
    ort = db.Column(db.Integer, nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String, nullable=False)
    kuerzel = db.Column(db.String, nullable=False)
    kartennummer = db.Column(db.String, nullable=False)
    pin = db.Column(db.String, nullable=False)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class LoginOPin(FlaskForm):
    kartennummer = StringField("Bitte Karte Eingeben")


class LoginWPin(FlaskForm):
    kuerzel = StringField("Kürzel", validators=[Length(1), DataRequired()])
    pin = PasswordField("PIN", validators=[DataRequired()])
    einloggen = SubmitField("Einloggen")

class KeyFinder(FlaskForm):
    nummer = IntegerField("Nummer")
    schluesselname = StringField("Name")


@app.route("/", methods=["GET", "POST"])
def login():
    form = LoginOPin()
    if request.method == "POST":
        print(form.kartennummer.data)
        user = User.query.filter_by(kartennummer=form.kartennummer.data).first()
        if user:
            login_user(user)
            return redirect(url_for("userPanel"))
        
    return render_template("login.html", form=form)

@app.route('/pinLogin', methods=["GET", "POST"])
def pinLogin():
    form = LoginWPin()
    if request.method == "POST":
        try:
            user = User.query.filter_by(kuerzel=form.kuerzel.data).first()
            check_pin = check_password(form.pin.data, user.pin)
            if user and check_pin:
                login_user(user)
                return redirect(url_for("userPanel"))
            else:
                flash("Falsches Kürzel oder Pin", "danger")
        except AttributeError:
            flash("Bitte alle Felder ausfüllen", "warning")
    return render_template('loginPin.html', form = form)

@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/userPanel", methods=["GET", "POST"])
@login_required
def userPanel():
    return render_template("userPanel.html", current_user=current_user)

@app.route("/keyFinder", methods=["GET", "POST"])
@login_required
def keyFinder():
    form = KeyFinder()
    return render_template("keyFinder.html", form=form)



if __name__ == "__main__":
    app.run("0.0.0.0", "5000", debug=True)

    