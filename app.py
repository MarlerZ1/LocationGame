import os

import sqlalchemy
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from dotenv import load_dotenv
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash

load_dotenv()

app = Flask(__name__)


class Config:
    SECRET_KEY = 'devkey'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'mysql://{os.getenv("DB_USER")}:{os.getenv("MYSQL_ROOT_PASSWORD")}@{os.getenv("DB_ADDRESS")}/{os.getenv("DB_NAME")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


app.config.from_object(Config)

db = SQLAlchemy(app)


class User(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    name = db.mapped_column(db.String(32), unique=True)
    password = db.mapped_column(db.Text)
    position = relationship("Position",back_populates="user")
    position_id = db.mapped_column(db.ForeignKey("position_table.id"))


class Position(db.Model):
    __tablename__ = "position_table"
    id = db.mapped_column(db.Integer, primary_key=True)
    user = relationship("User", uselist=False, back_populates="position")

    x = db.mapped_column(db.Integer)
    y = db.mapped_column(db.Integer)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/registration', methods=["POST", "GET"])
def registration():
    if request.method == "POST":
        if len(request.form['login']) > 2 and request.form['password'] == request.form['repeat_password']:
            try:
                psw_hash = generate_password_hash(request.form['password'])
                p = Position(x=0, y=0)
                db.session.add(p)
                u = User(name=request.form['login'], password=psw_hash, position=p)
                db.session.add(u)
                db.session.commit()
            except sqlalchemy.exc.IntegrityError as e:
                db.session.rollback()
                print("There is a login dublicate:\n ", e)


    return render_template('registration.html')


admin = Admin(app, name='LocationGame', template_mode='bootstrap4')
admin.add_view(ModelView(Position, db.session, name="Позиция"))

if __name__ == '__main__':
    app.app_context().push()
    db.create_all()
    app.run()
