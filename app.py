import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


class Config:
    SECRET_KEY = 'devkey'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'mysql://{os.getenv("DB_USER")}:{os.getenv("MYSQL_ROOT_PASSWORD")}@{os.getenv("DB_ADDRESS")}/{os.getenv("DB_NAME")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


app.config.from_object(Config)

db = SQLAlchemy(app)


class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Integer)
    y = db.Column(db.Integer)


@app.route('/')
def hello_world():
    return render_template('index.html')


admin = Admin(app, name='LocationGame', template_mode='bootstrap4')
admin.add_view(ModelView(Position, db.session, name="Позиция"))

if __name__ == '__main__':
    app.app_context().push()
    db.create_all()
    app.run()
