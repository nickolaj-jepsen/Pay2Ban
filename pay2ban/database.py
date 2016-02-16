from datetime import datetime

from flask import current_app
from sqlalchemy.ext.hybrid import hybrid_property

from pay2ban.module import db, bcrypt
from pay2ban.teamspeak import TeamspeakConnection


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    creation_date = db.Column(db.DateTime, nullable=False)
    password = db.Column(db.Binary(60), nullable=False)
    admin = db.Column(db.Boolean, default=False)

    payments = db.relationship("Payment", backref="user")
    actions = db.relationship("Action", backref="user")

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.creation_date = datetime.now()
        self.set_password(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    @property
    def balance(self):
        balance = 0
        for payment in self.payments:
            balance += payment.amount
        for action in self.actions:
            balance -= action.cost
        return balance

    def add_money(self, amount):
        self.payments.append(Payment(amount))

    def __repr__(self):
        return u'<User {}>'.format(self.name)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


class Payment(db.Model):
    __tablename__ = "payment"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    amount = db.Column(db.Numeric, nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    def __init__(self, amount):
        self.amount = amount
        self.time = datetime.now()


class Action(db.Model):
    __tablename__ = "action"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String, nullable=False)
    target_name = db.Column(db.String, nullable=False)
    target_id = db.Column(db.String, nullable=False)
    anon = db.Column(db.Boolean, nullable=False)
    cost = db.Column(db.Numeric, nullable=False)
    length = db.Column(db.Interval, nullable=True)
    time = db.Column(db.DateTime, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, action_type, target, length, anon):
        self.type = action_type
        self.target_id = target
        self.target_name = TeamspeakConnection(current_app.config['TS3_USERNAME'], current_app.config['TS3_PASSWORD']).name_from_cui(target)
        self.length = length
        self.anon = anon
        self.time = datetime.now()
        self.cost = self.calc_price()

    @hybrid_property
    def active(self):
        return self.time + self.length > datetime.now()

    def calc_price(self):
        cost = 0
        minutes = self.length.total_seconds() // 60

        if self.type == "kick" or self.type == "ban" or self.type == "mute":
            cost += 2

        if self.type == "ban":
            cost += minutes * 4

        if self.type == "mute":
            cost += minutes * 2

        if self.anon:
            cost += 2

        return cost

    def do_action(self):
        ts = TeamspeakConnection(current_app.config['TS3_USERNAME'], current_app.config['TS3_PASSWORD'])
        length = int(self.length.total_seconds()) // 60

        if self.type == "kick":
            if self.anon:
                ts.kick_user(self.target_id)
            else:
                ts.kick_user(self.target_id, reason="You were kicked by {} from pay2ban.nickolaj.com".format(self.user.name))
        elif self.type == "mute":
            ts.mute(self.target_id)
            db.session.commit()
        else:
            if self.anon:
                ts.ban_user(self.target_id, length)
            else:
                ts.ban_user(self.target_id, length, reason="You were kicked by {} from pay2ban.nickolaj.com".format(self.user.name))
        ts.close()