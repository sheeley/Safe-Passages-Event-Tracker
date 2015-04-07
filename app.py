from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)


def render(content):
    return render_template("base.html", content=content)


@app.route("/")
def add():
    key = "AIzaSyAF_o9iMtsGlET7yYVhAWoLFsRGBU9ge4o"
    date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    content = render_template("map.html", key=key, date=date)
    return render(content)


@app.route("/save")
def save():
    pass


@app.route("/list")
def list_existing():
    pass


if __name__ == "__main__":
    app.run(debug=True)
