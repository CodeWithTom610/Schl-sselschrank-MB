# Importiere notwendige Module und Bibliotheken
import os  # Betriebssystem-Funktionen
import platform  # Plattforminformationen (z. B. Windows, Linux)
from flask import Flask, render_template, request, redirect, url_for, flash  # Flask-Funktionen
from flask_bootstrap import Bootstrap5  # Bootstrap-Integration für Flask
from flask_wtf import FlaskForm  # Flask-WTF für Formulare
from wtforms import StringField, PasswordField, IntegerField, SubmitField  # Formularfelder
from wtforms.validators import Length, DataRequired  # Validierungsregeln für Formulare
from flask_sqlalchemy import SQLAlchemy  # SQLAlchemy für Datenbankintegration
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user  # Login-Management
from utils import hash_password, check_password  # Benutzerdefinierte Funktionen für Passwort-Hashing
from flask_bcrypt import Bcrypt  # Bcrypt für Passwort-Hashing

# Initialisiere die Flask-App
app = Flask(__name__, static_url_path='/static')

# Konfiguriere die App
app.config['SECRET_KEY'] = '55c02bd01e10ebbedf78e48c395e91451923c377'  # Geheimschlüssel für Sitzungen
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"  # SQLite-Datenbank
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Deaktiviere unnötige Warnungen

# Initialisiere Bootstrap, Login-Manager und Datenbank
bootstrap = Bootstrap5(app)  # Bootstrap-Integration
login_manager = LoginManager()  # Login-Manager für Benutzerverwaltung
login_manager.init_app(app)  # Login-Manager mit der App verbinden
login_manager.login_view = "login"  # Standard-Login-Ansicht
db = SQLAlchemy()  # SQLAlchemy-Objekt erstellen
db.init_app(app)  # SQLAlchemy mit der App verbinden
bcrypt = Bcrypt(app)  # Bcrypt für Passwort-Hashing

# Datenbankmodell für Schlüssel
class Schlüssel(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)  # Eindeutige ID
    nummer = db.Column(db.Integer, nullable=False)  # Schlüsselnummer
    schluesselname = db.Column(db.String, nullable=False)  # Schlüsselname
    ort = db.Column(db.Integer, nullable=False)  # Ort des Schlüssels

# Datenbankmodell für Benutzer
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, unique=True)  # Eindeutige ID
    name = db.Column(db.String, nullable=False)  # Benutzername
    kuerzel = db.Column(db.String, nullable=False)  # Kürzel des Benutzers
    kartennummer = db.Column(db.String, nullable=False)  # Kartennummer
    pin = db.Column(db.String, nullable=False)  # Gehashte PIN

# Erstelle die Datenbanktabellen, falls sie noch nicht existieren
with app.app_context():
    db.create_all()

# Benutzerladefunktion für Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)  # Lade Benutzer anhand der ID

# Formular für Login mit Karte
class LoginOPin(FlaskForm):
    kartennummer = StringField("Bitte Karte Eingeben")  # Eingabefeld für Kartennummer

# Formular für Login mit PIN
class LoginWPin(FlaskForm):
    kuerzel = StringField("Kürzel", validators=[Length(1), DataRequired()])  # Eingabefeld für Kürzel
    pin = PasswordField("PIN", validators=[DataRequired()])  # Eingabefeld für PIN
    einloggen = SubmitField("Einloggen")  # Absenden-Button

# Formular für Schlüssel-Suche
class KeyFinder(FlaskForm):
    nummer = IntegerField("Nummer")  # Eingabefeld für Schlüsselnummer
    schluesselname = StringField("Name")  # Eingabefeld für Schlüsselname

# Route für Login mit Karte
@app.route("/", methods=["GET", "POST"])
def login():
    form = LoginOPin()  # Initialisiere das Formular
    if request.method == "POST":
        print(form.kartennummer.data)  # Debug-Ausgabe der Kartennummer
        user = User.query.filter_by(kartennummer=form.kartennummer.data).first()  # Suche Benutzer
        if user:
            login_user(user)  # Benutzer einloggen
            return redirect(url_for("userPanel"))  # Weiterleitung zum Benutzer-Panel
    return render_template("login.html", form=form)  # Login-Seite anzeigen

# Route für Login mit PIN
@app.route('/pinLogin', methods=["GET", "POST"])
def pinLogin():
    form = LoginWPin()  # Initialisiere das Formular
    if request.method == "POST":
        try:
            user = User.query.filter_by(kuerzel=form.kuerzel.data).first()  # Suche Benutzer
            check_pin = check_password(form.pin.data, user.pin)  # Überprüfe PIN
            if user and check_pin:
                login_user(user)  # Benutzer einloggen
                return redirect(url_for("userPanel"))  # Weiterleitung zum Benutzer-Panel
            else:
                flash("Falsches Kürzel oder Pin", "danger")  # Fehlermeldung
        except AttributeError:
            flash("Bitte alle Felder ausfüllen", "warning")  # Warnung bei fehlenden Eingaben
    return render_template('loginPin.html', form=form)  # Login-Seite mit PIN anzeigen

# Route für Logout
@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()  # Benutzer ausloggen
    return redirect(url_for('login'))  # Weiterleitung zur Login-Seite

# Route für Benutzer-Panel
@app.route("/userPanel", methods=["GET", "POST"])
@login_required
def userPanel():
    return render_template("userPanel.html", current_user=current_user)  # Benutzer-Panel anzeigen

# Route für Schlüssel-Suche
@app.route("/keyFinder", methods=["GET", "POST"])
@login_required
def keyFinder():
    form = KeyFinder()  # Initialisiere das Formular
    if request.method == "POST":
        if form.nummer.data == None:
            key = Schlüssel.query.filter_by(schluesselname=form.schluesselname.data).first()  # Suche Schlüssel nach Name
        else:
            key = Schlüssel.query.filter_by(nummer=form.nummer.data).first()  # Suche Schlüssel nach Nummer
        
        if key:
            return render_template("keyFinder_after.html", key=key)  # Zeige Schlüssel-Details
        else:
            flash("Schlüssel nicht gefunden", "warning")  # Fehlermeldung
    return render_template("keyFinder.html", form=form)  # Schlüssel-Suche anzeigen

# Route für persönliche Einstellungen
@app.route('/personalSettings')
@login_required
def persSettings():
    user = current_user  # Aktueller Benutzer
    return render_template("personalSettings.html", user=user)  # Persönliche Einstellungen anzeigen

# Route für das Ändern der Kartennummer
@app.route('/change/card', methods=["GET", "POST"])
@login_required
def reread_card():
    user = current_user  # Aktueller Benutzer
    form = LoginOPin()  # Initialisiere das Formular
    if request.method == "POST":
        user = User.query.filter_by(name=current_user.name).first()  # Suche Benutzer
        new_karennummer = hash_password(form.kartennummer.data)  # Hash die neue Kartennummer
        user.kartennummer = new_karennummer  # Aktualisiere Kartennummer
        db.session.commit()  # Änderungen speichern
        flash("Karte wurde erfolgreich gespeichert", "success")  # Erfolgsmeldung
        return redirect(url_for('persSettings'))  # Weiterleitung zu persönlichen Einstellungen
    return render_template('changeCardNumber.html', user=user)  # Seite für Kartennummer ändern anzeigen

# Route für das Ändern der PIN
@app.route('/change/pin', methods=["GET", "POST"])
@login_required
def change_pin():
    user = current_user  # Aktueller Benutzer
    if request.method == "POST":
        user = User.query.filter_by(name=current_user.name).first()  # Suche Benutzer
        new_pin = hash_password(request.form['pin'])  # Hash die neue PIN
        user.pin = new_pin  # Aktualisiere PIN
        db.session.commit()  # Änderungen speichern
        flash("Pin wurde erfolgreich geändert", "success")  # Erfolgsmeldung
        return redirect(url_for('persSettings'))  # Weiterleitung zu persönlichen Einstellungen
    return render_template('changePin.html', user=user)  # Seite für PIN ändern anzeigen

# Route für das Ändern des Namens
@app.route('/change/name', methods=["GET", "POST"])
@login_required
def change_name():
    user = current_user  # Aktueller Benutzer
    if request.method == "POST":
        user = User.query.filter_by(name=current_user.name).first()  # Suche Benutzer
        user.name = request.form['name']  # Aktualisiere Name
        db.session.commit()  # Änderungen speichern
        flash("Name wurde erfolgreich geändert", "success")  # Erfolgsmeldung
        return redirect(url_for('persSettings'))  # Weiterleitung zu persönlichen Einstellungen
    return render_template('changeName.html', user=user)  # Seite für Name ändern anzeigen

# Route für das Ändern des Kürzels
@app.route('/change/kuerzel', methods=["GET", "POST"])
@login_required
def change_kuerzel():
    user = current_user  # Aktueller Benutzer
    if request.method == "POST":
        user = User.query.filter_by(name=current_user.name).first()  # Suche Benutzer
        user.kuerzel = request.form['kuerzel']  # Aktualisiere Kürzel
        db.session.commit()  # Änderungen speichern
        flash("Kürzel wurde erfolgreich geändert", "success")  # Erfolgsmeldung
        return redirect(url_for('persSettings'))  # Weiterleitung zu persönlichen Einstellungen
    return render_template('changeKuerzel.html', user=user)  # Seite für Kürzel ändern anzeigen

# Route für Systemeinstellungen
@app.route('/system/settings', methods=["GET", "POST"])
@login_required
def systemSettings():
    return render_template('systemSettings.html')  # Systemeinstellungen anzeigen

# Route für Debug-Modus
@app.route('/system/debug', methods=["GET", "POST"])
@login_required
def systemDebug():
    return render_template('debugMode.html')  # Debug-Modus anzeigen

# Route für System-Shutdown
@app.route('/system/shutdown', methods=["GET", "POST"])
@login_required
def shutdown():
    o_s = platform.system()  # Betriebssystem ermitteln
    if o_s == "Windows":
        return os.system("shutdown /s /t 1")  # Shutdown-Befehl für Windows
    else:
        return os.system("sudo shutdown now")  # Shutdown-Befehl für Linux
    
# Route für das Hinzufügen von Schlüsseln
@app.route('/add/key/<nummer>/<name>/<ort>', methods=["GET", "POST"])
@login_required
def add_key(nummer, name, ort):
    # Erstellt ein neues Schlüssel-Objekt mit den übergebenen Parametern
    new_key = Schlüssel(nummer=nummer, schluesselname=name, ort=ort)
    db.session.add(new_key)  # Fügt das neue Schlüssel-Objekt zur Datenbank hinzu
    db.session.commit()  # Speichert die Änderungen in der Datenbank
    return f"Schlüssel wurde erfolgreich hinzugefügt mit der Nummer {nummer}, dem Namen {name} und dem Ort {ort}"
    # Gibt eine Erfolgsmeldung zurück

# Route für das Hinzufügen von Benutzern
@app.route('/create/user/<name>/<kuerzel>/<kartennummer>/<pin>', methods=["GET", "POST"])
@login_required
def add_user(name, kuerzel, kartennummer, pin):
    # Erstellt ein neues Benutzer-Objekt mit den übergebenen Parametern
    new_user = User(name=name, kuerzel=kuerzel, kartennummer=kartennummer, pin=hash_password(pin))
    db.session.add(new_user)  # Fügt das neue Benutzer-Objekt zur Datenbank hinzu
    db.session.commit()  # Speichert die Änderungen in der Datenbank
    return f"Benutzer wurde erfolgreich hinzugefügt mit dem Namen {name}, dem Kürzel {kuerzel}, der Kartennummer {kartennummer} und der PIN {pin}"
    # Gibt eine Erfolgsmeldung zurück

# Route für das Löschen von Schlüsseln
@app.route('/delete/key/<nummer>', methods=["GET", "POST"])
@login_required
def delete_key(nummer):
    # Sucht den Schlüssel anhand der Nummer in der Datenbank
    key = Schlüssel.query.filter_by(nummer=nummer).first()
    db.session.delete(key)  # Löscht den gefundenen Schlüssel aus der Datenbank
    db.session.commit()  # Speichert die Änderungen in der Datenbank
    return f"Schlüssel mit der Nummer {nummer} wurde erfolgreich gelöscht"
    # Gibt eine Erfolgsmeldung zurück

# Route für das Löschen von Benutzern
@app.route('/delete/user/<name>', methods=["GET", "POST"])
@login_required
def delete_user(name):
    # Sucht den Benutzer anhand des Namens in der Datenbank
    user = User.query.filter_by(name=name).first()
    db.session.delete(user)  # Löscht den gefundenen Benutzer aus der Datenbank
    db.session.commit()  # Speichert die Änderungen in der Datenbank
    return f"Benutzer mit dem Namen {name} wurde erfolgreich gelöscht"
    # Gibt eine Erfolgsmeldung zurück

# Starte die Flask-App
if __name__ == "__main__":
    app.run("0.0.0.0", "5000", debug=True)  # App im Debug-Modus starten