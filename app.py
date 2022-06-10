from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login.html")
def login():
    return render_template('login.html')

@app.route("/ticket.html")
def ticket():
    return render_template('ticket.html')

@app.route("/drop-off.html")
def dropoff():
    return render_template('drop-off.html')

@app.route("/cylinder-analysis.html")
def cyla():
    return render_template('cylinder-analysis.html')

@app.route("/cylinder-breaking.html")
def cylb():
    return render_template('cylinder-breaking.html')

@app.route("/create-report.html")
def creport():
    return render_template('create-report.html')


if __name__ == '__main__':
    app.run(debug=True)