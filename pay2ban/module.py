from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin, AdminIndexView

migrate = Migrate()
db = SQLAlchemy()
login_manager = LoginManager()
admin = Admin(index_view=AdminIndexView(url='/flask-admin'))
bcrypt = Bcrypt()
