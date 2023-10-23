from flask import Flask, Response, render_template, jsonify, request, abort
from flask_basicauth import BasicAuth
import subprocess
import sys
import os

import logging

import json

def read_json(path):
    with open(path) as f:
        return json.load(f)

app = Flask(__name__)

# Configure the Flask app logger
file_handler = logging.FileHandler('app/log/server.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', "%Y-%m-%d_%H:%M:%S"))
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

@app.errorhandler(451)
def page_unavailable_for_legal_reasons(error):
    return render_template('451.html'), 451

secrets_json_path = "secrets/secrets.json"

if not os.path.exists(secrets_json_path):
    os.mkdir("secrets")
    with open(secrets_json_path, 'w') as outfile:
        json.dump({"username": "", "password": ""}, outfile)
    print("Secrets file was missing. Enter username and password in secrets/secrets.json")
    sys.exit(1)

secrets = read_json(secrets_json_path)
settings = read_json("application.json")

app.config['BASIC_AUTH_USERNAME'] = secrets['username']
app.config['BASIC_AUTH_PASSWORD'] = secrets['password']

basic_auth = BasicAuth(app)

program_status = "not running"

def ip_is_valid():
    # get ip address
    ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    # check if ip starts with 141.54
    app.logger.info("Request from " + str(ip))
    if str(ip).startswith("141.54") or str(ip).startswith("127.0"):
        return True
    else:
        app.logger.warning("Rejected IP " + ip)
        return False
  

'''
-----------------------------------------------------

Section for App-specific functions

-----------------------------------------------------
'''
import pdfsearch

@app.route('/')
def index():
    print(request.remote_addr)
    if not ip_is_valid():
        abort(451)
    try:
        q = request.args.get('q')
        print("Seomeone searched for " + str(q))
        if len(q) > 3:
            results = pdfsearch.search(q)
        else:
            results = []
    except Exception as e:
        print(e)
        results = []

    if q is None:
        return render_template('landing_page.html')
    return render_template('search.html', results=results, query=q)

@app.route('/search')
def search():
    if not ip_is_valid():
        abort(451)
    try:
        q = request.args.get('q')
        print("Seomeone searched for " + str(q))
        if len(q) > 3:
            results = pdfsearch.search(q)
        else:
            results = []
    except Exception as e:
        print(e)
        results = []
    return render_template('search.html', results=results, query=q)

'''
-----------------------------------------------------

Section for template functions

-----------------------------------------------------
'''

@app.route('/secret')
@basic_auth.required
def secret_page():
    return "You have access to the secret page!"

@app.route('/status')
def status():
    global program_status
    return jsonify(status=program_status)

@app.route('/logs/application')
@basic_auth.required
def logs():
    log_messages = []
    with open('app/log/application.log', 'r') as logfile:
        for line in logfile:
            try:
                time, application, log_type, message = line.strip().split(' ', 3)
                log_messages.append({'time': time, 'application': application, 'type': log_type, 'message': message})
            except Exception as e:
                print("Parse Error for log event:" + line)
    log_messages = log_messages[::-1]  # Reverse the order of the messages to display the latest message first
    return render_template('logs.html', log_messages=log_messages)

@app.route('/logs/server')
@basic_auth.required
def server_logs():
    log_messages = []
    with open('app/log/server.log', 'r') as logfile:
        for line in logfile:
            try:
                time, application, log_type, message = line.strip().split(' ', 3)
                log_messages.append({'time': time, 'application': application, 'type': log_type, 'message': message})
            except Exception as e:
                print("Parse Error for log event:" + line)
    log_messages = log_messages[::-1]  # Reverse the order of the messages to display the latest message first
    return render_template('logs.html', log_messages=log_messages)


@app.route('/activate', methods=['POST'])
def activate():
    global program_status
    if program_status == "success":
        return jsonify(status='already running')
    program_running = True
    if start():
        program_status = "success"
    else:
        program_status = "failed"
    return jsonify(status=program_status)

def start():
    # code for your function goes here
    subprocess.Popen(["python", "app/main.py"]) 
    print("Subprocess initialized")
    return True

with app.app_context():
    if settings["autostart_enabled"]:
        print("Autostarting application...")
        app.logger.info("Autostarting application...")
        app_running = start()
        if app_running:
            program_status = "success"
        else:
            program_status = "failed"

if __name__ == '__main__':
    app.run()