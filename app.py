from flask import Flask, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import pymysql
import secrets


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:temppass@localhost/cylinders'
app.config['SECRET_KEY'] = "arrrrrrimasecretkeyarrrrrrrrr"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(days=14)

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column(db.String(20))

    def __init__(self, username):
        self.username = username

# class ticket(db.Model):
#     _batch_id = db.Column("Batch ID", db.String, primary_key=True)
#     username = db.Column(db.String(20))
#     notes
#     client_name
#     site_add
#     struct_grid
#     charge_time
#     spec_air
#     mold_type
#     cast_by
#     temp_min
#     temp_max
#     mix_id
#     load_no
#     spec_slump
#     subclient_contractor
#     cast_time
#     measured_air
#     truck_no
#     ticket_no
#     size_agg
#     conc_supp
#     meas_slump
#     spec_str
#     conc_temp
#     amb_temp
    

    def __init__(self, _batch_id):
        self._batch_id = _batch_id

class cylinder(db.Model):
    _SID = db.Column("SAFFA ID", db.String, primary_key=True)
    batch_id = db.Column(db.String(20))
    height
    weight
    dia
    comp_str
    frac_type


    def __init__(self, _SID):
        self._SID = _SID

@app.route("/", methods=["POST", "GET"])
def index():
    return render_template('index.html')

@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["username"]
        session["user"] = user
        
        found_user = users.query.filter_by(name=user).first()

        if found_user:
            return render_template('drop-off.html')
        else:
            user = users(user)
            db.session.add(user)
            db.session.commit()


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


@app.route("/view/")
def view():
    return render_template('view.html', values=users.query.all())

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
    db.create_all()
    app.run(debug=True)