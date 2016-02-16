import re

from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash
from flask_login import login_required, current_user

from pay2ban.database import User
from pay2ban.module import db

blueprint = Blueprint("api", __name__, template_folder="template", url_prefix="/api")


@blueprint.route("/user/<user_id>/balance", methods=["POST"])
@login_required
def update_balance(user_id):
    if current_user.admin:
        content = request.get_json(silent=True)
        User.query.get(user_id).add_money(content["amount"])
        db.session.commit()
        return "1"
    else:
        return "0"
