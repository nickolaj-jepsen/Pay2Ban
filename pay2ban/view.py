import re
import traceback

from datetime import timedelta

from sqlalchemy import desc

from pay2ban.database import User, Action
from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from pay2ban.module import db
from pay2ban.teamspeak import TeamspeakConnection

from pay2ban.utils import check_recaptcha

blueprint = Blueprint("view", __name__, template_folder="template")


@blueprint.route("/")
def index():
    ts = TeamspeakConnection(current_app.config['TS3_USERNAME'], current_app.config['TS3_PASSWORD'])
    users = ts.list_users()
    ts.close()
    return render_template("index.html", channels=users, actions=Action.query.order_by(desc(Action.time)).limit(4).all())


@blueprint.route("/register", methods=['GET', 'POST'])
def register():
    errors = {
        "username": None,
        "email": None,
        "password": None,
        "recaptcha": None
    }

    if request.method == 'POST':
        recaptcha_resp = request.form.get('g-recaptcha-response')
        username = request.form.get('username', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        password_repeat = request.form.get('passwordRepeat', '')

        if 3 >= len(username) <= 20:
            errors["username"] = "Brugernavnet skal være mellem 3 og 20 tegn langt"

        valid_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZÆØÅabcdefghijklmnopqrstuvwxyzæøå-_.1234567890"

        for char in username:
            if char not in valid_chars:
                errors["username"] = "Ulovlig tegn i brugernavn: " + char

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors["email"] = "Email kunne ikke valideres"

        if User.query.filter_by(name=username).scalar() is not None:
            errors["username"] = "Brugernavnet er allerede taget"

        if User.query.filter_by(email=email).scalar() is not None:
            errors["email"] = "Emailen er allerede brugt"

        if len(password) < 4:
            errors["password"] = "adgangskoden er for kort"

        if password != password_repeat:
            errors["password"] = "adgangskoderne er ikke ens"

        if not check_recaptcha(recaptcha_resp, current_app.config["RECAPTCHA_SECRET_KEY"]):
            errors["recaptcha"] = "Der var fejl i captcha'en, prøv igen"

        if not any([type(x) == str for x in errors.values()]):
            new_user = User(username, email, password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for("view.index"))

    return render_template("register.html", site_key=current_app.config["RECAPTCHA_SITE_KEY"], errors=errors)


@blueprint.route("/login", methods=['GET', 'POST'])
def login():
    error = False
    if request.method == 'POST':

        username = request.form.get('username', '')
        password = request.form.get('password', '')

        user = User.query.filter_by(name=username).scalar()

        if user is None:
            user = User.query.filter_by(email=username).scalar()

        if user is None:
            error = True
        else:
            if user.check_password(password):
                login_user(user, remember=True)
                return redirect(url_for("view.index"))
            else:
                error = True
    return render_template("login.html", error=error)


@blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("view.index"))


@blueprint.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
    errors = {
        "old_password": None,
        "new_password": None,
        "new_password_repeat": None
    }
    if request.method == 'POST':
        old_password = request.form.get('oldPassword', '')
        new_password = request.form.get('newPassword', '')
        new_password_repeat = request.form.get('newPasswordRepeat', '')

        if current_user.check_password(old_password):
            errors["old_password"] = "Det gamle kode er forket"

        print(new_password)
        if len(new_password) < 4:
            errors["new_password"] = "adgangskoden er for kort"

        if new_password_repeat != new_password_repeat:
            errors["new_password_repeat"] = "adgangskoderne er ikke ens"

        if not any([type(x) == str for x in errors.values()]):
            current_user.set_password(new_password)
            db.session.commit()
            flash("Din adgangskode er blevet ændret", "primary")
            return redirect(url_for("view.settings"))

    return render_template("settings.html", errors=errors)


@blueprint.route("/admin")
@login_required
def admin():
    if not current_user.admin:
        return redirect(url_for("view.index"))

    return render_template("admin.html", users=User.query.all())


@blueprint.route("/action", methods=["POST"])
@login_required
def action():
    try:
        action_type = request.form.get("actionType", "")
        target_id = request.form.get("targetId", "")
        minutes = timedelta(minutes=int(request.form.get("minutes", "")))
        anon = request.form.get("anon", "") == "on"

        if 1 <= (int(minutes.total_seconds()) // 60) >= 15:
            flash("Fejl under udførelsen af dit køb", "danger")
            return redirect(url_for("view.index"))

        if target_id in current_app.config["PROTECTED_CUI"]:
            flash("Fejl under udførelsen af dit køb", "danger")
            return redirect(url_for("view.index"))

        new_action = Action(action_type, target_id, minutes, anon)
        if current_user.balance >= new_action.cost:
            current_user.actions.append(new_action)
            new_action.do_action()
            db.session.add(new_action)
            db.session.commit()
            flash("Dit køb er udført", "primary")
        else:
            flash("Du har ikke nok penge på kontoen til dette køb", "danger")
    except Exception as e:
        traceback.print_exc()
        flash("Fejl under udførelsen af dit køb", "danger")

    return redirect(url_for("view.index"))
