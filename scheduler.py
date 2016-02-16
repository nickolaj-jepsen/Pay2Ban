import os

import time

from pay2ban.database import User, Action
from pay2ban.teamspeak import TeamspeakConnection

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from autoapp import app


engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])

session = sessionmaker()
session.configure(bind=engine)

s = session()

active_actions = {}

while True:
    result = s.query(Action).filter_by(active=True).all()
    current_active = {y.id: y for y in result}
    removed = set(active_actions.items()) - set(current_active.items())

    for removed_action in removed:
        if removed_action[1].type == "mute":
            TeamspeakConnection(app.config['TS3_USERNAME'], app.config['TS3_PASSWORD']).unmute(removed_action[1].target_id)

    active_actions = current_active
    time.sleep(5)
