from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from pay2ban.database import User, Payment, Action
from flask import Flask
from pay2ban.module import migrate, db, login_manager, admin, bcrypt

from pay2ban.view import blueprint
from pay2ban.api import blueprint as api


def create_app(config_file=None):
    app = Flask(__name__)

    if config_file:
        try:
            app.config.from_pyfile("config\\" + config_file)
        except FileNotFoundError:
            app.config.from_pyfile("config/" + config_file)
    else:
        from pay2ban import config
        app.config.from_pyfile(config)

    init_app(app)

    return app


def init_app(app):
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(blueprint=api)
    app.register_blueprint(blueprint=blueprint)
    login_manager.login_view = "view.login"
    bcrypt.init_app(app)
    init_admin(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


def init_admin(app):
    class AuthModelView(ModelView):
        def is_accessible(self):
            return current_user.is_authenticated and current_user.admin

    admin.init_app(app, endpoint="flask-admin", url="/flask-admin")
    admin.add_view(AuthModelView(User, db.session))
    admin.add_view(AuthModelView(Payment, db.session))
    admin.add_view(AuthModelView(Action, db.session))
