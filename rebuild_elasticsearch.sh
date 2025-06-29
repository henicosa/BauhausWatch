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

echo "Setup complete! The application should be available at http://localhost:5303"
echo "Elasticsearch is available at http://localhost:9200" 