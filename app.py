import datetime
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
        cur_day = datetime.date.today().strftime("%y")
        cur_mo = datetime.date.today().strftime("%m")


        crs.execute("""SELECT ticket_timestamp
                    FROM ticket
                    GROUP by ticket_timestamp
                    ORDER BY max(ticket_timestamp)
                    LIMIT 1""")
        
        month_online = crs.fetchone()
        
        if month_online is None:
            month_online = -1
        else:
            month_online = str(month_online[0])[5:-12]

        if month_online == -1 or int(cur_mo) > int(month_online):
            crs.execute("""UPDATE REF
                        SET _ref_no = 1""")
            db.commit()
        else:
            crs.execute("""UPDATE REF
                        SET _ref_no = _ref_no + 1""")
            db.commit()

        crs.execute("""SELECT _ref_no FROM REF""")
        increment = crs.fetchone()[0]

        
        bid = cur_day + "-" + cur_mo + str(increment).zfill(5)

        client = request.form["client"][2:-3]
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


        q1 = request.form["q1"]
        q2 = request.form["q2"]
        q3 = request.form["q3"]
        q4 = request.form["q4"]
        q5 = request.form["q5"]
        q6 = request.form["q6"]
        
        cb1 = request.form.get('eb1')
        cb2 = request.form.get('eb2')
        cb3 = request.form.get('eb3')
        cb4 = request.form.get('eb4')
        cb5 = request.form.get('eb5')
        cb6 = request.form.get('eb6')
        
        if cb1 is None:
            d1 = request.form["d1"]
        if cb2 is None:
            d2 = request.form["d2"]
        if cb3 is None:
            d3 = request.form["d3"]
        if cb4 is None:
            d4 = request.form["d4"]
        if cb5 is None:
            d5 = request.form["d5"]
        if cb6 is None:
            d6 = request.form["d6"]

        note = request.form["note_text"]
        username = "admin"



        crs.execute("""INSERT INTO ticket (_batch_id, username, notes, client_name, mix_id, ticket_no, site_add, load_no, agg_size, struct_grid, spec_slump, 
                    conc_supp, charge_time, subclient_cont, meas_slump, spec_air, cast_time, spec_str, mould_type, meas_air, conc_temp, cast_by, 
                    truck_no, amb_temp, temp_min, temp_max) VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                    (bid, username, note, client, mix, ticket, address, load, agg, gridlines, spec_sl, conc_sup, toc, subclient, meas_sl, spec_air, 
                    cast_time, spec_str, mould, meas_air, conc_temp, cast_by, truck_no, amb_temp, min_temp, max_temp))
        db.commit()

        sid = ""

        for i in range(1, int(q1) + 1):
            if cb1 is None:
                sid = bid + "A" + "-" + d1 + "D" + "-" + str(i)
            else:
                sid = bid + "A" + "-" + cb1 + "D" + "-" + str(i)
            crs.execute("""INSERT INTO Cylinder (_SID, batch_id) VALUES 
                        (%s, %s)""", 
                        (sid, bid))
            db.commit()
        
        if q2:
            for i in range(1, int(q2) + 1):
                if cb2 is None:
                    sid = bid + "B" + "-" + d2 + "D" + "-" + str(i)
                else:
                    sid = bid + "B" + "-" + cb2 + "D" + "-" + str(i)
                crs.execute("""INSERT INTO Cylinder (_SID, batch_id) VALUES 
                            (%s, %s)""", 
                            (sid, bid))
                db.commit()

        if q3:
            for i in range(1, int(q3) + 1):
                if cb3 is None:
                    sid = bid + "C" + "-" + d3 + "D" + "-" + str(i)
                else:
                    sid = bid + "C" + "-" + cb3 + "D" + "-" + str(i)
                crs.execute("""INSERT INTO Cylinder (_SID, batch_id) VALUES 
                            (%s, %s)""", 
                            (sid, bid))
                db.commit()

        if q4:
            for i in range(1, int(q4) + 1):
                if cb4 is None:
                    sid = bid + "D" + "-" + d4 + "D" + "-" + str(i)
                else:
                    sid = bid + "D" + "-" + cb4 + "D" + "-" + str(i)
                crs.execute("""INSERT INTO Cylinder (_SID, batch_id) VALUES 
                            (%s, %s)""", 
                            (sid, bid))
                db.commit()

        if q5:
            for i in range(1, int(q5) + 1):
                if cb5 is None:
                    sid = bid + "E" + "-" + d5 + "D" + "-" + str(i)
                else:
                    sid = bid + "E" + "-" + cb5 + "D" + "-" + str(i)
                crs.execute("""INSERT INTO Cylinder (_SID, batch_id) VALUES 
                            (%s, %s)""", 
                            (sid, bid))
                db.commit()

        if q6:
            for i in range(1, int(q6) + 1):
                if cb6 is None:
                    sid = bid + "F" + "-" + d6 + "D" + "-" + str(i)
                else:
                    sid = bid + "F" + "-" + cb6 + "D" + "-" + str(i)
                crs.execute("""INSERT INTO Cylinder (_SID, batch_id) VALUES 
                            (%s, %s)""", 
                            (sid, bid))
                db.commit()

        return f"<h1>GREAT SUCCESS { sid }</h1>"
        
        # return f"<h1>GREAT SUCCESS { cur_mo } and online mo: { month_online } and BID is { sid }</h1>"
    else:
        crs.execute("SELECT * FROM client")
        return render_template('ticket.html', value=crs.fetchall())

@app.route("/drop-off/", methods=["GET", "POST"])
def dropoff():
    if request.method == "POST":
        drop_id = request.form["drop_id"][2:-3]

        crs.execute("""UPDATE ticket  
                    SET dropoff_timestamp = CURRENT_TIMESTAMP
                    WHERE _batch_id = (%s)
                    """, (drop_id,))
        db.commit()
        return f"GOOD SUCCESS { drop_id }"
    else:
        crs.execute("SELECT _batch_id FROM ticket ORDER BY ticket_timestamp DESC")
        return render_template('drop-off.html', drop=crs.fetchall())


@app.route("/cylinder-analysis/")
def cyla():
    if request.method == "POST":
        # d1 = request.form["d1"]
        # d2 = request.form["d2"]
        # d3 = request.form["d3"]
        # d4 = request.form["d4"]
        # d5 = request.form["d5"]
        # d6 = request.form["d6"]

        # q1 = request.form["q1"]
        # q2 = request.form["q2"]
        # q3 = request.form["q3"]
        # q4 = request.form["q4"]
        # q5 = request.form["q5"]
        # q6 = request.form["q6"]

        # crs.execute("INSERT INTO user (_username, password) VALUES (%s, %s)", (user, hash_password))

        # crs.execute("INSERT INTO ticket (_batch_id, mix, ticket, address, load, agg, gridlines, spec_sl, "
        # "conc_sup, toc, subclient, meas_sl, spec_air, cast_time, spec_str, mould, meas_air, conc_temp, cast_by, "
        # "truck_no, amb_temp, min_temp, max_temp) VALUES"
        # "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
        # (batch_id, mix, ticket, address, load, agg, gridlines, spec_sl, conc_sup, toc, subclient, meas_sl, spec_air, 
        # cast_time, spec_str, mould, meas_air, conc_temp, cast_by, truck_no, amb_temp, min_temp, max_temp))
        # db.commit


        return f"<h1>hello</h1>"
    else:
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

@app.route("/test/", methods=["GET", "POST"])
def test():
    if request.method == "POST":
        tex1 = request.form["testdd"]
        return f"<h1>{ tex1 }</h1>"
    else:
        return render_template('test.html')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='localhost', port=5000)