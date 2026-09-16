from flask import Flask, render_template
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

from config import Config
from models import db, User
from routes.auth import auth
from routes.admin import admin
from routes.staff import staff
from routes.user import user

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.register_blueprint(auth)
app.register_blueprint(staff)
app.register_blueprint(admin)
app.register_blueprint(user)



@app.route("/")
def home():
    return render_template("home.html")


with app.app_context():

    db.create_all()

    admin = User.query.filter_by(
        email="admin@trek.com"
    ).first()

    if admin is None:

        admin = User(
            name="Administrator",
            email="admin@trek.com",
            password=generate_password_hash("admin123"),
            role="admin",
            status="approved"
        )

        db.session.add(admin)
        db.session.commit()


if __name__ == "__main__":
    app.run(debug=True)