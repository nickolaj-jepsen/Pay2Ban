import os

from pay2ban.app import create_app

if os.environ.get("FLASK_DEBUG", False) == "1":
    app = create_app("dev.py")
else:
    app = create_app("prod.py")
