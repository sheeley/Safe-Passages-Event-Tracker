from flask import Flask, render_template
app = Flask(__name__)


def render(content):
    return render_template("base.html", content=content)


@app.route("/")
def add():
    content = render_template("map.html")
    return render(content)

@app.route("/save")
def save():
    pass

@app.route("/list")
def list_existing():
    pass


if __name__ == "__main__":
    app.run(debug=True)
