import os

import sqlalchemy
from flask import Flask, render_template, request, url_for, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from dotenv import load_dotenv
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)


class Config:
    SECRET_KEY = 'devkey'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'mysql://{os.getenv("DB_USER")}:{os.getenv("MYSQL_ROOT_PASSWORD")}@{os.getenv("DB_ADDRESS")}/{os.getenv("DB_NAME")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


app.config.from_object(Config)

db = SQLAlchemy(app)
login_manager = LoginManager(app)


class UserLogin:
    def fromDB(self, user_id):
        self.__user = User.query.filter_by(id=user_id).first()
        return self

    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_admin(self):
        return self.__user.is_admin

    def get_id(self):
        return str(self.__user.id)


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id)


class User(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    name = db.mapped_column(db.String(32), unique=True, nullable=False)
    is_admin = db.mapped_column(db.Boolean, nullable=False)
    password = db.mapped_column(db.Text, nullable=False)
    position = relationship("Position", back_populates="user")
    position_id = db.mapped_column(db.ForeignKey("position_table.id"))


class Position(db.Model):
    __tablename__ = "position_table"
    id = db.mapped_column(db.Integer, primary_key=True)
    user = relationship("User", uselist=False, back_populates="position")

    x = db.mapped_column(db.Integer)
    y = db.mapped_column(db.Integer)


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(name=request.form['login']).first()

        if user and check_password_hash(str(user.password), str(request.form['password'])):
            userLogin = UserLogin().create(user)
            login_user(userLogin)
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/registration', methods=["POST", "GET"])
def registration():
    if request.method == "POST":
        if len(request.form['login']) > 2 and request.form['password'] == request.form['repeat_password']:
            try:
                psw_hash = generate_password_hash(request.form['password'])
                p = Position(x=0, y=0)
                db.session.add(p)
                u = User(name=request.form['login'], is_admin=False, password=psw_hash, position=p)
                db.session.add(u)
                db.session.commit()
            except sqlalchemy.exc.IntegrityError as e:
                db.session.rollback()
                print("There is a login dublicate:\n ", e)
            else:
                return redirect(url_for('login'))

    return render_template('registration.html')


class AdminMixin:
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))
        else:
            return redirect(url_for('index'))


class AdminView(AdminMixin, ModelView):
    pass


class HomeAdminView(AdminMixin, AdminIndexView):
    pass


admin = Admin(app, name='LocationGame', template_mode='bootstrap4', index_view=HomeAdminView(name="Home"))
admin.add_view(AdminView(Position, db.session, name="Позиция"))

if __name__ == '__main__':
    app.app_context().push()
    db.create_all()
    app.run()
