from .global_obj import app


@app.route("/hello")
def do_hello():
    return "123"
