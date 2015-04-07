from flask import Flask, render_template, jsonify, request

app = Flask(__name__)


def render(content):
    return render_template("base.html", content=content)


@app.route("/")
def add():
    key = "AIzaSyAF_o9iMtsGlET7yYVhAWoLFsRGBU9ge4o"
    content = render_template("map.html", key=key)
    return render(content)


@app.route("/save", methods=['POST'])
def save():
    form = request.form
    # TODO
    return jsonify({"success": True})


@app.route("/list")
def list_existing():
    pass


if __name__ == "__main__":
    app.run(debug=True)
