from flask import Flask, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "arrrrrrimasecretkeyarrrrrrrrr"
app.permanent_session_lifetime = timedelta(days=14)

@app.route("/", methods=["POST", "GET"])
def index():
    return render_template('index.html')

@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        # if user in username (database)
        session.permanent = True
        user = request.form["username"]
        session["user"] = user
        return redirect(url_for("user"))
    else:
        if "user" in session:
            return redirect(url_for("user"))
        return render_template('login.html')

@app.route("/user/")
def user():
    if "user" in session:
        user = session["user"]
        return f"<h1>{user}</h1>"
    else:
        return redirect(url_for("login"))

@app.route("/ticket/")
def ticket():
    return render_template('ticket.html')

@app.route("/drop-off/")
def dropoff():
    return render_template('drop-off.html')

@app.route("/cylinder-analysis/")
def cyla():
    return render_template('cylinder-analysis.html')

@app.route("/cylinder-breaking/")
def cylb():
    return render_template('cylinder-breaking.html')

@app.route("/create-report/")
def creport():
    return render_template('create-report.html')

@app.route("/register/")
def register():
    return redirect(url_for("index"))

@app.route("/logout/")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True)