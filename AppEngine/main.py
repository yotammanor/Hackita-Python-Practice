__author__ = 'TOSHIBA'
from bottle import route, run, default_app

@route('/')
def hello():
    return "Hello from bottle! :-)"

application = default_app()