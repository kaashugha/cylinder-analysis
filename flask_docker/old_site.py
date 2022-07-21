from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for, send_file

# BLUEPRINTS
app = Flask(__name__)

@app.route("/about-us/")
def aboutUs():
    return render_template('about-us.html')

@app.route("/careers/")
def careers():
    return render_template('careers.html')

@app.route("/contact-us/")
def contactUs():
    return render_template('contact-us.html')

@app.route("/index/")
def index():
    return render_template('index.html')

@app.route("/projects/")
def projects():
    return render_template('projects.html')

@app.route("/services/")
def projects():
    return render_template('services.html')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080, use_reloader=False)
