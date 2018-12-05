from flask import Flask

app = Flask(__name__)

env = app.config['ENV']
app.config.from_pyfile("config/common.py", silent=False)
if env.lower() == 'production':
    app.config.from_pyfile("config/production.py", silent=False)
else:
    app.config.from_pyfile("config/development.py", silent=False)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
