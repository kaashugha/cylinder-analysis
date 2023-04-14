import datetime
import glob
import io
import os
import shutil
from datetime import date, timedelta
from pathlib import Path
from typing import OrderedDict

import bcrypt
import gcalendar
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import mysql.connector
import report_pdf
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   send_file, send_from_directory, session, url_for)
from Google import Create_Service
from tabulate import tabulate

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
CALENDAR_ID = os.getenv('CALENDAR_ID')
SECRET_KEY = os.getenv('SECRET_KEY')

CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'calendar'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/calendar']

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=14)
app.secret_key = SECRET_KEY

DIRNAME = os.path.dirname(__file__)

db = mysql.connector.connect(
    host=os.getenv('HOST'),
    user=os.getenv('USERNAME'),
    passwd=os.getenv('PASSWORD'),
    database=os.getenv('DATABASE')
)
db.autocommit = True

def configure():
    load_dotenv()

def permission(user):
    try:
        crs = db.cursor(buffered=True)
    except:
        db.reconnect()
        crs = db.cursor(buffered=True)
    crs.execute("""SELECT role
                FROM user
                WHERE _username=%s
                """, [user])
    role = crs.fetchone()[0]
    crs.close()

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

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def service_build():
    # Load credentials from the session.
    creds = google.oauth2.credentials.Credentials(
        **session['credentials'])

    #drive = googleapiclient.discovery.build(
        #API_NAME, API_VERSION, credentials=credentials)

    # files = drive.files().list().execute()

    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    session['credentials'] = credentials_to_dict(creds)

    service = googleapiclient.discovery.build(API_NAME, API_VERSION, credentials=creds)

    return service

@app.route('/oauth2', methods=['GET', 'POST'])
def oauth2():
	# Use the client_secret.json file to identify the application requesting
	# authorization. The client ID (from that file) and access scopes are required.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=[SCOPES][0])

	# Indicate where the API server will redirect the user after the user completes
	# the authorization flow. The redirect URI is required. The value must exactly
	# match one of the authorized redirect URIs for the OAuth 2.0 client, which you
	# configured in the API Console. If this value doesn't match an authorized URI,
	# you will get a 'redirect_uri_mismatch' error.
    flow.redirect_uri = url_for('oauth2callback', _external=True)


	# Generate URL for request to Google's OAuth 2.0 server.
	# Use kwargs to set optional request parameters.
    authorization_url, state = flow.authorization_url(
		# Enable offline access so that you can refresh an access token without
		# re-prompting the user for permission. Recommended for web server apps.
		access_type='offline',
		# Enable incremental authorization. Recommended as a best practice.
		include_granted_scopes='true')

			# 	service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
	# 	print(API_SERVICE_NAME, API_VERSION, 'service created successfully')
	
    session['state'] = state

    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)
    
    return redirect(url_for('index'))

@app.route('/sid_list/', methods=['POST'])
def sid_list():
    try:
        crs = db.cursor(buffered=True)
    except:
        db.reconnect()
        crs = db.cursor(buffered=True)
    req = request.json
    bid = req.get('bid_ca')
    crs.execute("SELECT _SID FROM Cylinder WHERE batch_id=%s", [bid])
    sid = crs.fetchall()
    crs.close()
    return jsonify(sid)

@app.route('/test/', methods=['POST'])
def test():
    name=request.args.get('value')
    sid_list = name.split(",")

    bid_dict = {}
    bid_list = []

    for i in range(len(sid_list)):
        bid = sid_list[i][:10]
        bid_list.append(bid)
        sid = sid_list[i]
        if bid not in bid_dict:
            bid_dict[bid] = [sid]
        else:
            bid_dict[bid].append(sid)

    for bid in bid_dict:
        try:
            crs = db.cursor(buffered=True)
        except:
            db.reconnect()
            crs = db.cursor(buffered=True)
        sid = bid_dict[bid]
        format_strings = ','.join(['%s'] * len(sid))
        crs.execute("""SELECT
                    ticket._batch_id,
                    ticket.ticket_timestamp,
                    ticket.dropoff_timestamp,
                    ticket.client_name,
                    ticket.notes,
                    ticket.site_add,
                    ticket.struct_grid,
                    ticket.charge_time,
                    ticket.spec_air,
                    ticket.mould_type,
                    ticket.cast_by,
                    ticket.temp_min,
                    ticket.temp_max,
                    ticket.mix_id,
                    ticket.load_no,
                    ticket.spec_slump,
                    ticket.subclient_cont,
                    ticket.cast_time,
                    ticket.meas_air,
                    ticket.truck_no,
                    ticket.ticket_no,
                    ticket.agg_size,
                    ticket.conc_supp,
                    ticket.meas_slump,
                    ticket.spec_str,
                    ticket.conc_temp,
                    ticket.amb_temp,
                    ticket.plt,
                    ticket.cast_plt,
                    Cylinder._SID,
                    Cylinder.curing,
                    Cylinder.height,
                    Cylinder.weight,
                    Cylinder.dia,
                    Cylinder.comp_str,
                    Cylinder.frac_type,
                    Cylinder.receiving_date
                FROM
                    ticket
                JOIN Cylinder ON ticket._batch_id = Cylinder.batch_id
                    WHERE Cylinder._SID
                    IN (%s)"""  % format_strings, tuple(sid))

        test_res = crs.fetchall()
        crs.close()


        sid_dict = OrderedDict()

        sid_dict["Lab No"] = []
        sid_dict["Casting Date"] = []
        sid_dict["Receiving Date"] = []
        sid_dict["Curing"] = []
        sid_dict["Age"] = []
        sid_dict["Testing Date"] = []
        sid_dict["Diameter (mm)"] = []
        sid_dict["Mass of Cylinder (g)"] = []
        sid_dict["Density (kg/m3)"] = []
        sid_dict["Compressive Strength (MPa)"] = []
        sid_dict["Type of Fracture*"] = []

        # Takes batch information from first cylinder
        batch_data = {
        '_batch_id': test_res[0][0],
        'client_name': test_res[0][3],
        'notes': test_res[0][4],
        'site_add': test_res[0][5],
        'struct_grid': test_res[0][6],
        'charge_time': test_res[0][7],
        'spec_air': test_res[0][8],
        'mould_type': test_res[0][9],
        'cast_by': test_res[0][10],
        'temp_min': test_res[0][11],
        'temp_max': test_res[0][12],
        'mix_id': test_res[0][13],
        'load_no': test_res[0][14],
        'spec_slump': test_res[0][15],
        'subclient_cont': test_res[0][16],
        'cast_time': test_res[0][17],
        'meas_air': test_res[0][18],
        'truck_no': test_res[0][19],
        'ticket_no': test_res[0][20],
        'agg_size': test_res[0][21],
        'conc_supp': test_res[0][22],
        'meas_slump': test_res[0][23],
        'spec_str': test_res[0][24],
        'conc_temp': test_res[0][25],
        'amb_temp': test_res[0][26],
        'plt': test_res[0][27],
        'cast_plt': test_res[0][28]
        }
        
        for i in range(len(test_res)):
            ticket_timestamp = str(test_res[i][1])[:-9]

            if test_res[i][2]:
                dropoff_timestamp = str(test_res[i][2])[:-9]
            else:
                dropoff_timestamp = ""

            _SID = test_res[i][29]
            curing = test_res[i][30]

            if test_res[i][31]:
                height = test_res[i][31]
            else:
                height = ""

            if test_res[i][32]:
                weight = test_res[i][32]
            else:
                weight = ""

            if test_res[i][33]:
                dia = test_res[i][33]
            else:
                dia = ""

            if test_res[i][34]:
                comp_str = test_res[i][34]
            else:
                comp_str = ""

            if test_res[i][35]:    
                frac_type = test_res[i][35]
            else:
                frac_type = ""
            
            if test_res[i][36]:
                testing_date = str(test_res[i][36])[:-16]
            else:
                testing_date = ""

            if test_res[i][32] and test_res[i][33] and test_res[i][31]:
                density = round((float(weight) / (3.14159265 * float(dia / 2) ** 2 * float(height))) * 1000000)
            else:
                density = ""

            sid_dict["Lab No"].append(_SID)
            sid_dict["Casting Date"].append(ticket_timestamp)
            sid_dict["Receiving Date"].append(dropoff_timestamp)
            sid_dict["Curing"].append(curing)
            sid_dict["Age"].append(_SID[12:].split('D', 1)[0])
            sid_dict["Testing Date"].append(testing_date)
            sid_dict["Diameter (mm)"].append(dia)
            sid_dict["Mass of Cylinder (g)"].append(weight)
            sid_dict["Density (kg/m3)"].append(density)
            sid_dict["Compressive Strength (MPa)"].append(comp_str)
            sid_dict["Type of Fracture*"].append(frac_type)

        report_pdf.create_pdf(sid_dict, batch_data)

    user = session['user']


    filename = 'reports'
    dir_zip = os.path.join(DIRNAME, 'static/Reports', '')
    dir_dest = os.path.join(DIRNAME, f'static/Zip/{ user }', '')

    # os.remove(dir_dest + 'reports.zip')
    # os.rmdir(dir_dest)

    # Creates users folder in zip folder if it doesnt exist
    if not os.path.isdir(dir_dest):
        os.mkdir(dir_dest)
        

    shutil.make_archive(os.path.join(dir_dest, filename), 'zip', dir_zip)

    # Delete all reports generated in Reports file
    [f.unlink() for f in Path(dir_zip).glob("*") if f.is_file()]

    return jsonify({'reply':'success'})

@app.route("/employee-portal", methods=["POST", "GET"])
def empPortal():
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
        try:
            crs = db.cursor(buffered=True)
        except:
            db.reconnect()
            crs = db.cursor(buffered=True)
        session.permanent = True
        user = request.form["username"]

        crs.execute("SELECT password FROM user WHERE _username=%s", [user])
        hash_password = crs.fetchone()
        crs.close()

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
            return redirect(url_for('empPortal'))

        return render_template('login.html')


@app.route("/register/", methods=['POST', 'GET'])
def register():
    if not login_check():
        return redirect(url_for("login"))

    role = permission(session['user'])

    if role == 'admin':
        if request.method == "POST":
            try:
                crs = db.cursor(buffered=True)
            except:
                db.reconnect()
                crs = db.cursor(buffered=True)
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

            crs.close()

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

    if 'credentials' not in session:
        return redirect(url_for("oauth2"))
    else:
        service = service_build()

    if request.method == "POST":
        try:
            crs = db.cursor(buffered=True)
        except:
            db.reconnect()
            crs = db.cursor(buffered=True)
        cur_mo = datetime.date.today().strftime("%m")
        cur_year = datetime.date.today().strftime("%y")

        crs.execute("""SELECT ticket_timestamp
                    FROM ticket
                    GROUP by ticket_timestamp
                    ORDER BY ticket_timestamp DESC
                    LIMIT 1""")

        month_online = crs.fetchone()
        crs.close()

        if month_online is None:
            month_online = -1
        else:
            month_online = str(month_online[0])[5:-12]


        crs = db.cursor(buffered=True)
        if month_online == -1 or int(cur_mo) > int(month_online):
            crs.execute("""UPDATE REF
                        SET _ref_no = 1""")
            db.commit()
        else:
            crs.execute("""UPDATE REF
                        SET _ref_no = _ref_no + 1""")
            db.commit()
        crs.close()


        crs = db.cursor(buffered=True)
        crs.execute("""SELECT _ref_no FROM REF""")
        increment = crs.fetchone()[0]
        crs.close()

        bid = cur_year + "-" + cur_mo + str(increment).zfill(5)

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

        if request.form["plt"]:
            plt = request.form["plt"]
            if request.form.get("cast_plt"):
                cast_plt = "Yes"
            else:
                cast_plt = "No"
        else:
            plt = "N/A"
            cast_plt = "N/A"


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


        crs = db.cursor(buffered=True)
        crs.execute("""INSERT INTO ticket (_batch_id, ticket_gen_username, notes, client_name, mix_id, ticket_no, site_add, load_no, agg_size, struct_grid, spec_slump, 
                    conc_supp, charge_time, subclient_cont, meas_slump, spec_air, cast_time, spec_str, mould_type, meas_air, conc_temp, cast_by, 
                    truck_no, amb_temp, temp_min, temp_max, plt, cast_plt) VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (bid, username, note, client, mix, ticket, address, load, agg, gridlines, spec_sl, conc_sup, toc, subclient, meas_sl, spec_air,
                     cast_time, spec_str, mould, meas_air, conc_temp, cast_by, truck_no, amb_temp, min_temp, max_temp, plt, cast_plt))
        db.commit()
        crs.close()
        sid = ""
        all_sid = []

        for i in range(1, int(q1) + 1):
            crs = db.cursor(buffered=True)
            sid = ""
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
            
            all_sid.append(sid)
            break_date = date.today() + relativedelta(days=+ int(sid[12:].split('D', 1)[0]))

            day= str(break_date)[8:]
            month = str(break_date)[5:-3]
            year = str(break_date)[:-6]
            
            eventID = gcalendar.cal_insert(int(day), int(month), int(year), sid, 5, user, service)
            crs.execute("""UPDATE Cylinder 
                        SET eventID = (%s)
                        WHERE _SID = (%s) 
                        """,
                        [eventID, sid])
            db.commit()
            crs.close()

        if q2:
            for i in range(1, int(q2) + 1):
                sid = ""
                crs = db.cursor(buffered=True)
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
                
                all_sid.append(sid)
                break_date = date.today() + relativedelta(days=+ int(sid[12:].split('D', 1)[0]))

                day= str(break_date)[8:]
                month = str(break_date)[5:-3]
                year = str(break_date)[:-6]
                
                eventID = gcalendar.cal_insert(int(day), int(month), int(year), sid, 5, user, service)
                crs.execute("""UPDATE Cylinder 
                            SET eventID = (%s)
                            WHERE _SID = (%s) 
                            """,
                            [eventID, sid])
                db.commit()
                crs.close()


        if q3:
            for i in range(1, int(q3) + 1):
                sid = ""
                crs = db.cursor(buffered=True)
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

                all_sid.append(sid)
                break_date = date.today() + relativedelta(days=+ int(sid[12:].split('D', 1)[0]))

                day= str(break_date)[8:]
                month = str(break_date)[5:-3]
                year = str(break_date)[:-6]

                eventID = gcalendar.cal_insert(int(day), int(month), int(year), sid, 5, user, service)
                crs.execute("""UPDATE Cylinder 
                            SET eventID = (%s)
                            WHERE _SID = (%s) 
                            """,
                            [eventID, sid])
                db.commit()
                crs.close()


        if q4:
            for i in range(1, int(q4) + 1):
                sid = ""
                crs = db.cursor(buffered=True)
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

                all_sid.append(sid)
                break_date = date.today() + relativedelta(days=+ int(sid[12:].split('D', 1)[0]))

                day= str(break_date)[8:]
                month = str(break_date)[5:-3]
                year = str(break_date)[:-6]

                eventID = gcalendar.cal_insert(int(day), int(month), int(year), sid, 5, user, service)
                crs.execute("""UPDATE Cylinder 
                            SET eventID = (%s)
                            WHERE _SID = (%s) 
                            """,
                            [eventID, sid])
                db.commit()
                crs.close()

        if q5:
            for i in range(1, int(q5) + 1):
                sid = ""
                crs = db.cursor(buffered=True)
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

                all_sid.append(sid)
                break_date = date.today() + relativedelta(days=+ int(sid[12:].split('D', 1)[0]))

                day= str(break_date)[8:]
                month = str(break_date)[5:-3]
                year = str(break_date)[:-6]

                eventID = gcalendar.cal_insert(int(day), int(month), int(year), sid, 5, user, service)
                crs.execute("""UPDATE Cylinder 
                            SET eventID = (%s)
                            WHERE _SID = (%s) 
                            """,
                            [eventID, sid])
                db.commit()
                crs.close()

        if q6:
            for i in range(1, int(q6) + 1):
                sid = ""
                crs = db.cursor(buffered=True)
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

                all_sid.append(sid)
                break_date = date.today() + relativedelta(days=+ int(sid[12:].split('D', 1)[0]))

                day= str(break_date)[8:]
                month = str(break_date)[5:-3]
                year = str(break_date)[:-6]

                eventID = gcalendar.cal_insert(int(day), int(month), int(year), sid, 5, user, service)
                crs.execute("""UPDATE Cylinder 
                            SET eventID = (%s)
                            WHERE _SID = (%s) 
                            """,
                            [eventID, sid])
                db.commit()
                crs.close()


        return render_template('ticket_success.html', bid=bid, all_sid=all_sid)

    else:
        try:
            crs = db.cursor(buffered=True)
        except:
            db.reconnect()
            crs = db.cursor(buffered=True)
        crs.execute("SELECT * FROM client")
        value = crs.fetchall()
        crs.close()
        return render_template('ticket.html', value=value)


@app.route("/drop-off/", methods=["GET", "POST"])
def dropoff():
    if not login_check():
        return redirect(url_for("login"))

    if 'credentials' not in session:
        return redirect(url_for("oauth2"))
    else:
        service = service_build()

    if request.method == "POST":
        try:
            crs = db.cursor(buffered=True)
        except:
            db.reconnect()
            crs = db.cursor(buffered=True)
        drop_id = request.form["drop_id"]
        user = session["user"]

        crs.execute("""UPDATE ticket  
                    SET dropoff_timestamp = CURRENT_TIMESTAMP, dropoff_username = %s
                    WHERE _batch_id = (%s)
                    """, [user, drop_id])
        db.commit()
        crs.close()


        crs = db.cursor(buffered=True)
        crs.execute(
            "SELECT eventID FROM Cylinder WHERE batch_id=%s", [drop_id])
        event_tuple = crs.fetchall()
        crs.close()

        for eventId in event_tuple:
            gcalendar.cal_update(*eventId, 7, service)

        return render_template('dropoff_success.html', bid=drop_id)
    else:
        try:
            crs = db.cursor(buffered=True)
        except:
            db.reconnect()
            crs = db.cursor(buffered=True)
        crs.execute(
            "SELECT _batch_id FROM ticket ORDER BY ticket_timestamp DESC")
        drop = crs.fetchall()
        crs.close()
        return render_template('drop-off.html', drop=drop)


@app.route("/cylinder-analysis/", methods=["GET", "POST"])
def cyla():    
    if not login_check():
        return redirect(url_for("login"))

    role = permission(session['user'])

    if role == 'admin' or role == 'lab':
        if request.method == "POST":
            try:
                crs = db.cursor(buffered=True)
            except:
                db.reconnect()
                crs = db.cursor(buffered=True)
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
            crs.close()

            return render_template('cylinder-analysis.html')
        else:
            try:
                crs = db.cursor(buffered=True)
            except:
                db.reconnect()
                crs = db.cursor(buffered=True)
            crs.execute(
                "SELECT _batch_id FROM ticket ORDER BY ticket_timestamp DESC")
            bid_cax = crs.fetchall()
            crs.close()
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
            try:
                crs = db.cursor(buffered=True)
            except:
                db.reconnect()
                crs = db.cursor(buffered=True)

            sid = request.form.get("sid_ca")
            comp_str = request.form.get("cstr")
            tof = request.form.get("tof")
            user = session["user"]

            crs.execute("""UPDATE Cylinder  
                SET comp_str = %s, frac_type = %s, breaking_username = %s
                WHERE _SID = (%s)
                """, [comp_str, tof, user, sid])
            db.commit()
            crs.close()

            return render_template('cylinder-breaking.html')

        else:
            try:
                crs = db.cursor(buffered=True)
            except:
                db.reconnect()
                crs = db.cursor(buffered=True)
            crs.execute(
                "SELECT _batch_id FROM ticket ORDER BY ticket_timestamp DESC")
            bid_cax = crs.fetchall()
            crs.close()

            return render_template('cylinder-breaking.html', bid_cax=bid_cax)
    else:
        return "<h1>Error: Insufficient Permissions to Access Page</h1>"

@app.route("/create-report/", methods=['GET', 'POST'])
def creport():
    if not login_check():
        return redirect(url_for("login"))

    if request.method == "POST":
        # Prompt user to download zip file of generated reports
        user = session['user']
        dir_dest = f'static/Zip/{ user }'

        full_path = os.path.join(app.root_path, dir_dest)

        return send_from_directory(
            full_path,
            'reports.zip',
            as_attachment=True,
        )
        
    else:
        user = session['user']
        dir_dest = os.path.join(DIRNAME, f'static/Zip/{ user }', '')
        
        if os.path.isdir(dir_dest):
            os.remove(dir_dest + 'reports.zip')
            os.rmdir(dir_dest)

        
        try:
            crs = db.cursor(buffered=True)
        except:
            db.reconnect()
            crs = db.cursor(buffered=True)
        crs.execute(
            "SELECT _batch_id FROM ticket ORDER BY ticket_timestamp DESC")
        bid_cax = crs.fetchall()
        crs.close()

        crs = db.cursor(buffered=True)
        crs.execute("""SELECT _batch_id, ticket_timestamp, client_name, site_add, subclient_cont 
                    FROM ticket 
                    ORDER BY ticket_timestamp DESC
                    LIMIT 500""")

        result = crs.fetchall()
        crs.close()
        fin = [['Batch ID', 'Date', 'Client', 'Site Address', 'Contractor']]

        for i in range(len(result)):
            res_list = []
            for j in range(5):
                res_list.append(result[i][j])
            fin.append(res_list)
        
        fintabulate = tabulate(fin,headers='firstrow',tablefmt='html')

        fintabulate = '<table id="search_data">' + fintabulate[7:]


        
        return render_template('create-report.html', bid_cax=bid_cax, search_data_html=fintabulate)

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

@app.route("/ticket_success/")
def ticket_success():
    return render_template('ticket_success.html')

@app.route("/dropoff_success/")
def dropoff_success():
    return render_template('dropoff_success.html')

@app.route("/about-us/")
def aboutUs():
    return render_template('about-us.html')

@app.route("/careers/")
def careers():
    return render_template('careers.html')

@app.route("/contact-us/")
def contactUs():
    return render_template('contact-us.html')

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/projects/")
def projects():
    return render_template('projects.html')

@app.route("/services/")
def services():
    return render_template('services.html')

if __name__ == '__main__':
    configure()
    app.run(debug=False, host=os.getenv('HOST'), port=8080, use_reloader=False)