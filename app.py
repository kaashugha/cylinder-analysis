from logging import warning
from flask import Flask, flash, get_flashed_messages, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import mysql.connector
import bcrypt

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=14)
app.secret_key = 'arrrimasecretkeyarrrrrr'

db = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='',
    database='cylinders'
)

crs = db.cursor(buffered=True)

@app.route("/", methods=["POST", "GET"])
def index():
    return render_template('index.html')

@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["username"]
        
        crs.execute("SELECT password FROM user WHERE _username=%s", [user])
        hash_password = crs.fetchone()[0]
        session["user"] = user
        
        if bcrypt.checkpw(request.form["password"].encode('utf-8'), hash_password):
            return redirect(url_for("index"))
        else:
            flash("Incorrect username or password.")
            return render_template('login.html')
        
        # return redirect(url_for("user"))
    else:
        if "user" in session:
            return redirect(url_for("index"))
        return render_template('login.html')

@app.route("/user/")
def user():
    if "user" in session:
        user = session["user"]
        return f"<h1>{user}</h1>"
    else:
        return redirect(url_for("login"))

@app.route("/register/", methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        session.permanent = True
        user = request.form["newuser"]
        password = request.form["newpass"].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
        
        crs.execute("SELECT * FROM user WHERE _username=%s", [user])

        if crs.rowcount == 0:
            crs.execute("INSERT INTO user (_username, password) VALUES (%s, %s)", (user, hash_password))
            db.commit()
            flash(f"User {user} created.")
        else:
            flash("User already exists. Please select a different username.")

        return redirect(url_for("register"))
    else:
        return render_template('register.html')

@app.route("/view/")
def view():
    return render_template('view.html', values=users.query.all())

@app.route("/ticket/", methods=['GET', 'POST'])
def ticket():
    if request.method == "POST":
        client = request.form["client"]
        mix = request.form["mix"]
        ticket = request.form["ticket"]
        address = request.form["address"]
        load = request.form["load"]
        agg = request.form["agg"]
        gridlines = request.form["gridlines"]
        spec_sl = request.form["spec_sl"]
        conc_sup = request.form["conc_sup"]
        toc = request.form["toc"]
        subclient = request.form["subclient"]
        meas_sl = request.form["meas_sl"]
        spec_air = request.form["spec_air"]
        cast_time = request.form["cast_time"]
        spec_str = request.form["spec_str"]
        mould = request.form["mould"]
        meas_air = request.form["meas_air"]
        conc_temp = request.form["conc_temp"]
        cast_by = request.form["cast_by"]
        truck_no = request.form["truck_no"]
        amb_temp = request.form["amb_temp"]
        min_temp = request.form["min_temp"]
        max_temp = request.form["max_temp"]

        crs.execute("INSERT INTO ticket (_batch_id) VALUES (%s)", (client,))
    else:
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

@app.route("/logout/")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='localhost', port=5000)