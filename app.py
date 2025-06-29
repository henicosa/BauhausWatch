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

# Create log directories if they don't exist
os.makedirs('app/log', exist_ok=True)
os.makedirs('log', exist_ok=True)

# Configure the Flask app logger
file_handler = logging.FileHandler('app/log/server.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', "%Y-%m-%d_%H:%M:%S"))
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# Configure the query logger with a different file handler
query_logger = logging.getLogger('query_logger')
query_logger.setLevel(logging.INFO)
query_file_handler = logging.FileHandler('app/log/query.log')
# only log date in query log
query_file_handler.setFormatter(logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s', "%Y-%m-%d"))
query_logger.addHandler(query_file_handler)


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

def get_stats():
    stats = {}
    amount = 5
    protocols = read_json("app/protocols.json")
    # sort by date
    protocols = sorted(protocols, key=lambda x: x['unixdate'], reverse=True)
    stats["recent_protocols"] = protocols[:amount]
    stats["total_protocols"] = len(protocols)
    stats["total_committees"] = len(set([x['committee'] for x in protocols]))
    return stats

def ip_is_valid():
    # get ip address
    ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    return True
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

# Try to import elasticsearch, but don't fail if it's not available
try:
    from elasticsearch import Elasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False
    app.logger.warning("Elasticsearch not available. Install with: pip install elasticsearch")

def search_protocols(query):
    # log query
    query_logger.info(query)
    
    # Get search engine from configuration
    search_engine = settings.get('search_engine', 'pdfsearch')
    
    if search_engine == 'elasticsearch':
        if not ELASTICSEARCH_AVAILABLE:
            app.logger.error("Elasticsearch requested but not available")
            return []
        return search_with_elasticsearch(query)
    else:
        # Default to pdfsearch
        return search_with_pdfsearch(query)

def search_with_pdfsearch(query):
    """Search using the original pdfsearch module"""
    try:
        results = pdfsearch.search(query)
        return results
    except Exception as e:
        app.logger.error(f"Error in pdfsearch: {e}")
        return []

def search_with_elasticsearch(query):
    """Search using Elasticsearch"""
    try:
        # Get Elasticsearch configuration from settings
        es_config = settings.get('elasticsearch', {})
        
        # Use environment variables if available (for container deployment)
        es_host = os.environ.get('ELASTICSEARCH_HOST', 'localhost')
        es_port = os.environ.get('ELASTICSEARCH_PORT', '9200')
        
        # Override with config if not using environment variables
        if es_host == 'localhost':
            hosts = es_config.get('hosts', ['http://localhost:9200'])
        else:
            hosts = [f"http://{es_host}:{es_port}"]
            
        timeout = es_config.get('timeout', 30)
        index = es_config.get('index', 'protocols')
        
        # Configure Elasticsearch connection
        es = Elasticsearch(hosts, timeout=timeout)
        
        # Define the search query
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["content", "title", "committee"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            },
            "highlight": {
                "fields": {
                    "content": {},
                    "title": {}
                }
            },
            "size": 20
        }
        
        # Perform the search
        response = es.search(index=index, body=search_body)
        
        # Format results to match the expected structure
        results = []
        for hit in response['hits']['hits']:
            result = {
                'title': hit['_source'].get('title', ''),
                'committee': hit['_source'].get('committee', ''),
                'date': hit['_source'].get('date', ''),
                'score': hit['_score'],
                'highlights': hit.get('highlight', {}),
                'content': hit['_source'].get('content', '')[:500] + '...' if len(hit['_source'].get('content', '')) > 500 else hit['_source'].get('content', '')
            }
            results.append(result)
        
        return results
        
    except Exception as e:
        app.logger.error(f"Error in Elasticsearch search: {e}")
        return []

@app.route('/')
def index():
    print(request.remote_addr)
    if not ip_is_valid():
        abort(451)
    try:
        q = request.args.get('q')
        if len(q) > 3:
            results = search_protocols(q)
        else:
            results = []
    except Exception as e:
        print(e)
        results = []

    if q is None:
        return render_template('landing_page.html', stats=get_stats())
    return render_template('search.html', results=results, query=q)

@app.route('/search')
def search():
    if not ip_is_valid():
        abort(451)
    try:
        q = request.args.get('q')
        if len(q) > 3:
            results = search_protocols(q)
        else:
            results = []
    except Exception as e:
        print(e)
        results = []
    return render_template('search.html', results=results, query=q)

# Alternative search endpoint that always uses Elasticsearch
@app.route('/search/elasticsearch')
def search_elasticsearch():
    if not ip_is_valid():
        abort(451)
    if not ELASTICSEARCH_AVAILABLE:
        return jsonify({"error": "Elasticsearch not available"}), 503
    
    try:
        q = request.args.get('q')
        if len(q) > 3:
            results = search_with_elasticsearch(q)
        else:
            results = []
    except Exception as e:
        app.logger.error(f"Error in elasticsearch endpoint: {e}")
        results = []
    
    return render_template('search.html', results=results, query=q)

# Alternative search endpoint that always uses pdfsearch
@app.route('/search/pdfsearch')
def search_pdfsearch():
    if not ip_is_valid():
        abort(451)
    
    try:
        q = request.args.get('q')
        if len(q) > 3:
            results = search_with_pdfsearch(q)
        else:
            results = []
    except Exception as e:
        app.logger.error(f"Error in pdfsearch endpoint: {e}")
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

@app.route('/logs/query')
@basic_auth.required
def query_logs():
    log_messages = []
    with open('app/log/query.log', 'r') as logfile:
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