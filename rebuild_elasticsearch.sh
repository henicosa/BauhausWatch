#!/bin/bash

echo "Stopping existing containers..."
docker-compose down

echo "Removing old images..."
docker rmi bauhauswatch:latest 2>/dev/null || true

echo "Building new image with Elasticsearch support..."
docker-compose build

echo "Starting services..."
docker-compose up -d

echo "Waiting for services to be ready..."
sleep 30

echo "Checking service status..."
docker-compose ps

echo "Checking Elasticsearch health..."
curl -s http://localhost:9200/_cluster/health | jq . 2>/dev/null || echo "Elasticsearch not ready yet"

echo "Rebuilding Elasticsearch index..."

# Get Elasticsearch configuration
ES_HOST=${ELASTICSEARCH_HOST:-localhost}
ES_PORT=${ELASTICSEARCH_PORT:-9200}

# Delete the existing index if it exists
echo "Deleting existing protocols index..."
curl -X DELETE "http://${ES_HOST}:${ES_PORT}/protocols" 2>/dev/null || echo "Index did not exist or could not be deleted"

# Wait a moment for the deletion to complete
sleep 2

# Run the data loader to recreate the index
echo "Loading data into Elasticsearch..."
python app/elasticsearch_loader.py

echo "Elasticsearch rebuild complete!"

echo "Setup complete! The application should be available at http://localhost:5303"
echo "Elasticsearch is available at http://localhost:9200" 