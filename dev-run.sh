#!/bin/bash

echo "Starting BauhausWatch Development Server..."

# Check if we're in a dev container
if [ -f "/.dockerenv" ]; then
    echo "Running in development container"
    
    # Wait for Elasticsearch if needed
    echo "Checking Elasticsearch connection..."
    python -c "
import time
from elasticsearch import Elasticsearch
es = Elasticsearch(['http://elasticsearch:9200'])
for i in range(30):
    try:
        if es.ping():
            print('Elasticsearch is ready!')
            break
        time.sleep(2)
    except:
        time.sleep(2)
else:
    print('Warning: Elasticsearch not ready, but continuing...')
"
    
    # Load data if index is empty
    echo "Checking if data needs to be loaded..."
    python -c "
from elasticsearch import Elasticsearch
es = Elasticsearch(['http://elasticsearch:9200'])
try:
    count = es.count(index='protocols')['count']
    print(f'Found {count} documents in Elasticsearch')
    if count == 0:
        print('Loading data into Elasticsearch...')
        import subprocess
        subprocess.run(['python', 'app/elasticsearch_loader.py'], check=True)
except:
    print('Loading data into Elasticsearch...')
    import subprocess
    subprocess.run(['python', 'app/elasticsearch_loader.py'], check=True)
"
    
    # Start Flask in development mode
    echo "Starting Flask development server..."
    export FLASK_ENV=development
    export FLASK_DEBUG=1
    python app.py
else
    echo "Not running in container. Please use the dev container setup."
    exit 1
fi 