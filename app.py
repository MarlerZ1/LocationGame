from flask import Flask, render_template

app = Flask(__name__)

class Config:
    SECRET_KEY = 'devkey'
    DEBUG = True

app.config.from_object(Config)

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()