import datetime
from flask import Flask, flash, get_flashed_messages, jsonify, redirect, render_template, request, session, url_for
from datetime import timedelta
import mysql.connector
import bcrypt
import gcalendar
from dotenv import load_dotenv
import os
import report_pdf
from tabulate import tabulate

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
CALENDAR_ID = os.getenv('CALENDAR_ID')
SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=14)
app.secret_key = SECRET_KEY

db = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='',
    database='cylinders'
)

crs = db.cursor(buffered=True)

def configure():
    load_dotenv()

def permission(user):
    crs.execute("""SELECT role
                FROM user
                WHERE _username=%s
                """, [user])
    role = crs.fetchone()[0]

    if role == 'admin':
        return 'admin'
    elif role == 'lab':
        return 'lab'
    else:
        return 'field'

def login_check():
    if "user" in session:
        user = session["user"]
        return user
    else:
        return



@app.route('/sid_list/', methods=['POST'])
def sid_list():

    req = request.json
    bid = req.get('bid_ca')[2:-3]
    crs.execute("SELECT _SID FROM Cylinder WHERE batch_id=%s", [bid])
    sid = crs.fetchall()
    return jsonify(sid)

@app.route('/test/', methods=['POST'])
def test():
    name=request.args.get('value')
    bid_list = name.split(",")

    format_strings = ','.join(['%s'] * len(bid_list))

    crs.execute("""SELECT _batch_id, ticket_timestamp, client_name, site_add, subclient_cont 
                FROM ticket 
                WHERE _batch_id
                IN (%s)"""  % format_strings, tuple(bid_list))
    test_res = crs.fetchall()
    print(test_res)


    return jsonify({'reply':'success'})


@app.route("/", methods=["POST", "GET"])
def index():
    if not login_check():
        return redirect(url_for("login"))

    role = permission(session['user'])

    if role == 'admin':
        return redirect(url_for('a'))
    elif role == 'lab':
        return redirect(url_for('l'))
    else:
        return redirect(url_for('f'))
        
@app.route("/a/", methods=["POST", "GET"])
def a():
    if not login_check():
        return redirect(url_for("login"))

    role = permission(session['user'])

    if role == 'admin':
        return render_template('adminindex.html')
    else:
        return "<h1>Error: Insufficient Permissions to Access Page</h1>"


@app.route("/l/", methods=["POST", "GET"])
def l():
    if not login_check():
        return redirect(url_for("login"))

    role = permission(session['user'])

    if role == 'lab' or role == 'admin':
        return render_template('labindex.html')
    else:
        return "<h1>Error: Insufficient Permissions to Access Page</h1>"

@app.route("/f/", methods=["POST", "GET"])
def f():
    if not login_check():
        return redirect(url_for("login"))

    return render_template('fieldindex.html')


@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["username"]

        crs.execute("SELECT password FROM user WHERE _username=%s", [user])
        hash_password = crs.fetchone()
        if hash_password is None:
            flash("Incorrect username or password.")
            return render_template('login.html')
        session["user"] = user


        if bcrypt.checkpw(request.form["password"].encode('utf-8'), *hash_password):
            role = permission(session['user'])

            if role == 'admin':
                return redirect(url_for('a'))
            elif role == 'lab':
                return redirect(url_for('l'))
            else:
                return redirect(url_for('f'))
        else:
            flash("Incorrect username or password.")
            return render_template('login.html')

    else:
        if "user" in session:
            return redirect(url_for('index'))

        return render_template('login.html')


@app.route("/register/", methods=['POST', 'GET'])
def register():
    if not login_check():
        return redirect(url_for("login"))

    role = permission(session['user'])

    if role == 'admin':
        if request.method == "POST":
            session.permanent = True
            user = request.form["newuser"]
            password = request.form["newpass"].encode('utf-8')
            hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
            acc_type = request.form["acctype"]

            crs.execute("SELECT * FROM user WHERE _username=%s", [user])

            if crs.rowcount == 0:
                crs.execute(
                    "INSERT INTO user (_username, password, role) VALUES (%s, %s, %s)", (user, hash_password, acc_type))
                db.commit()
                flash(f"User {user} created.")
            else:
                flash("User already exists. Please select a different username.")

            return redirect(url_for("register"))
        else:
            return render_template('register.html')
    else:
        return "<h1>Error: Insufficient Permissions to Access Page</h1>"

@app.route("/ticket/", methods=['GET', 'POST'])
def ticket():
    if not login_check():
        return redirect(url_for("login"))

    user = session["user"]

    if request.method == "POST":
        cur_day = datetime.date.today().strftime("%d")
        cur_mo = datetime.date.today().strftime("%m")
        cur_year = datetime.date.today().strftime("%y")

        crs.execute("""SELECT ticket_timestamp
                    FROM ticket
                    GROUP by ticket_timestamp
                    ORDER BY ticket_timestamp DESC
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

        bid = cur_year + "-" + cur_mo + str(increment).zfill(5)

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
        username = user

        crs.execute("""INSERT INTO ticket (_batch_id, ticket_gen_username, notes, client_name, mix_id, ticket_no, site_add, load_no, agg_size, struct_grid, spec_slump, 
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
                crs.execute("""INSERT INTO Cylinder (_SID, batch_id) VALUES 
                            (%s, %s)""",
                            (sid, bid))
                db.commit()
            else:
                sid = bid + "A" + "-" + cb1 + "D" + "-" + str(i)
                crs.execute("""INSERT INTO Cylinder (_SID, batch_id, curing) VALUES 
                            (%s, %s, %s)""",
                            (sid, bid, "On-Site"))
                db.commit()
            
            eventID = gcalendar.cal_insert(int(cur_day), int(cur_mo), cur_year, sid, 5, user)
            crs.execute("""UPDATE Cylinder 
                        SET eventID = (%s)
                        WHERE _SID = (%s) 
                        """,
                        [eventID, sid])
            db.commit()

        if q2:
            for i in range(1, int(q2) + 1):
                if cb2 is None:
                    sid = bid + "B" + "-" + d2 + "D" + "-" + str(i)
                    crs.execute("""INSERT INTO Cylinder (_SID, batch_id) VALUES 
                                (%s, %s)""",
                                (sid, bid))
                    db.commit()
                else:
                    sid = bid + "B" + "-" + cb2 + "D" + "-" + str(i)
                    crs.execute("""INSERT INTO Cylinder (_SID, batch_id, curing) VALUES 
                                (%s, %s, %s)""",
                                (sid, bid, "On-Site"))
                    db.commit()
                
                eventID = gcalendar.cal_insert(int(cur_day), int(cur_mo), cur_year, sid, 5, user)
                crs.execute("""UPDATE Cylinder 
                            SET eventID = (%s)
                            WHERE _SID = (%s) 
                            """,
                            [eventID, sid])
                db.commit()


        if q3:
            for i in range(1, int(q3) + 1):
                if cb3 is None:
                    sid = bid + "C" + "-" + d3 + "D" + "-" + str(i)
                    crs.execute("""INSERT INTO Cylinder (_SID, batch_id) VALUES 
                                (%s, %s)""",
                                (sid, bid))
                    db.commit()
                else:
                    sid = bid + "C" + "-" + cb3 + "D" + "-" + str(i)
                    crs.execute("""INSERT INTO Cylinder (_SID, batch_id, curing) VALUES 
                                (%s, %s, %s)""",
                                (sid, bid, "On-Site"))
                    db.commit()

                eventID = gcalendar.cal_insert(int(cur_day), int(cur_mo), cur_year, sid, 5, user)
                crs.execute("""UPDATE Cylinder 
                            SET eventID = (%s)
                            WHERE _SID = (%s) 
                            """,
                            [eventID, sid])
                db.commit()


        if q4:
            for i in range(1, int(q4) + 1):
                if cb4 is None:
                    sid = bid + "D" + "-" + d4 + "D" + "-" + str(i)
                    crs.execute("""INSERT INTO Cylinder (_SID, batch_id) VALUES 
                                (%s, %s)""",
                                (sid, bid))
                    db.commit()
                else:
                    sid = bid + "D" + "-" + cb4 + "D" + "-" + str(i)
                    crs.execute("""INSERT INTO Cylinder (_SID, batch_id, curing) VALUES 
                                (%s, %s, %s)""",
                                (sid, bid, "On-Site"))
                    db.commit()

                eventID = gcalendar.cal_insert(int(cur_day), int(cur_mo), cur_year, sid, 5, user)
                crs.execute("""UPDATE Cylinder 
                            SET eventID = (%s)
                            WHERE _SID = (%s) 
                            """,
                            [eventID, sid])
                db.commit()

        if q5:
            for i in range(1, int(q5) + 1):
                if cb5 is None:
                    sid = bid + "E" + "-" + d5 + "D" + "-" + str(i)
                    crs.execute("""INSERT INTO Cylinder (_SID, batch_id) VALUES 
                                (%s, %s)""",
                                (sid, bid))
                    db.commit()
                else:
                    sid = bid + "E" + "-" + cb5 + "D" + "-" + str(i)
                    crs.execute("""INSERT INTO Cylinder (_SID, batch_id, curing) VALUES 
                                (%s, %s, %s)""",
                                (sid, bid, "On-Site"))
                    db.commit()

                eventID = gcalendar.cal_insert(int(cur_day), int(cur_mo), cur_year, sid, 5, user)
                crs.execute("""UPDATE Cylinder 
                            SET eventID = (%s)
                            WHERE _SID = (%s) 
                            """,
                            [eventID, sid])
                db.commit()

        if q6:
            for i in range(1, int(q6) + 1):
                if cb6 is None:
                    sid = bid + "F" + "-" + d6 + "D" + "-" + str(i)
                    crs.execute("""INSERT INTO Cylinder (_SID, batch_id) VALUES 
                                (%s, %s)""",
                                (sid, bid))
                    db.commit()
                else:
                    sid = bid + "F" + "-" + cb6 + "D" + "-" + str(i)
                    crs.execute("""INSERT INTO Cylinder (_SID, batch_id, curing) VALUES 
                                (%s, %s, %s)""",
                                (sid, bid, "On-Site"))
                    db.commit()

                eventID = gcalendar.cal_insert(int(cur_day), int(cur_mo), cur_year, sid, 5, user)
                crs.execute("""UPDATE Cylinder 
                            SET eventID = (%s)
                            WHERE _SID = (%s) 
                            """,
                            [eventID, sid])
                db.commit()


        return f"<h1>GREAT SUCCESS { sid }</h1>"

    else:
        crs.execute("SELECT * FROM client")
        return render_template('ticket.html', value=crs.fetchall())


@app.route("/drop-off/", methods=["GET", "POST"])
def dropoff():
    if not login_check():
        return redirect(url_for("login"))

    if request.method == "POST":
        drop_id = request.form["drop_id"][2:-3]
        user = session["user"]

        crs.execute("""UPDATE ticket  
                    SET dropoff_timestamp = CURRENT_TIMESTAMP, dropoff_username = %s
                    WHERE _batch_id = (%s)
                    """, [user, drop_id])
        db.commit()

        crs.execute(
            "SELECT eventID FROM Cylinder WHERE batch_id=%s", [drop_id])
        event_tuple = crs.fetchall()

        for eventId in event_tuple:
            gcalendar.cal_update(*eventId, 7)

        return f"GOOD SUCCESS { drop_id }"
    else:
        crs.execute(
            "SELECT _batch_id FROM ticket ORDER BY ticket_timestamp DESC")
        return render_template('drop-off.html', drop=crs.fetchall())


@app.route("/cylinder-analysis/", methods=["GET", "POST"])
def cyla():    
    if not login_check():
        return redirect(url_for("login"))

    role = permission(session['user'])

    if role == 'admin' or role == 'lab':
        if request.method == "POST":
            
            sid = request.form.get("sid_ca")
            weight = request.form.get("weight")
            height = request.form.get("height")
            dia = request.form.get("dia")
            user = session["user"]

            crs.execute("""UPDATE Cylinder  
                SET height = %s, weight = %s, dia = %s, analysis_username = %s
                WHERE _SID = (%s)
                """, [height, weight, dia, user, sid])
            db.commit()

            return render_template('cylinder-analysis.html')
        else:
            crs.execute(
                "SELECT _batch_id FROM ticket ORDER BY ticket_timestamp DESC")
            bid_cax = crs.fetchall()

            return render_template('cylinder-analysis.html', bid_cax=bid_cax)

    else:
        return "<h1>Error: Insufficient Permissions to Access Page</h1>"


@app.route("/cylinder-breaking/", methods=["GET", "POST"])
def cylb():
    if not login_check():
        return redirect(url_for("login"))

    role = permission(session['user'])

    if role == 'admin' or role == 'lab':
        if request.method == "POST":

            sid = request.form.get("sid_ca")
            comp_str = request.form.get("cstr")
            tof = request.form.get("tof")
            user = session["user"]

            crs.execute("""UPDATE Cylinder  
                SET comp_str = %s, frac_type = %s, breaking_username = %s
                WHERE _SID = (%s)
                """, [comp_str, tof, user, sid])
            db.commit()

            return render_template('cylinder-breaking.html')

        else:
            crs.execute(
                "SELECT _batch_id FROM ticket ORDER BY ticket_timestamp DESC")
            bid_cax = crs.fetchall()

            return render_template('cylinder-breaking.html', bid_cax=bid_cax)
    else:
        return "<h1>Error: Insufficient Permissions to Access Page</h1>"

@app.route("/create-report/", methods=['GET', 'POST'])
def creport():
    if not login_check():
        return redirect(url_for("login"))
    
    role = permission(session['user'])

    if role == 'admin' or role == 'lab':
        role = permission(session['user'])

        if request.method == "POST":
            bid_list = request.form.get("selected_id")
            print(bid_list)

            # format_strings = ','.join(['%s'] * len(bid_list))

            # crs.execute("""SELECT _batch_id, ticket_timestamp, client_name, site_add, subclient_cont 
            #             FROM ticket 
            #             WHERE _batch_id
            #             IN (%s)"""  % format_strings, tuple(bid_list))
            # test_res = crs.fetchall()
            # print(test_res)
            return "GOOD SUCCESS post"
        else:
            crs.execute(
                "SELECT _batch_id FROM ticket ORDER BY ticket_timestamp DESC")
            bid_cax = crs.fetchall()

            batch_id = '22-0600001'

            # ticket_timestamp,
            # ORDER BY ticket_timestamp DESC

            crs.execute("""SELECT _batch_id, ticket_timestamp, client_name, site_add, subclient_cont 
                        FROM ticket 
                        ORDER BY ticket_timestamp DESC
                        LIMIT 500""")

            result = crs.fetchall()

            fin = [['Batch ID', 'Date', 'Client', 'Site Address', 'Contractor']]

            for i in range(len(result)):
                res_list = []
                for j in range(5):
                    res_list.append(result[i][j])
                fin.append(res_list)
            
            fintabulate = tabulate(fin,headers='firstrow',tablefmt='html')

            fintabulate = '<table id="search_data">' + fintabulate[7:]


            
            return render_template('create-report.html', bid_cax=bid_cax, search_data_html=fintabulate)

    else:
        return "<h1>Error: Insufficient Permissions to Access Page</h1>"


@app.route("/logout/")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/calendar/")
def calendar():
    if not login_check():
        return redirect(url_for("login"))
    
    role = permission(session['user'])

    google_key = GOOGLE_API_KEY
    calendar_key = CALENDAR_ID

    if role == 'admin' or role == 'lab':
        return render_template('calendar.html', google_key = google_key, calendar_key = calendar_key)
    else:
        return "<h1>Error: Insufficient Permissions to Access Page</h1>"


if __name__ == '__main__':
    configure()
    app.run(debug=True, host='localhost', port=5000)
