#!/bin/bash

echo "Setting up BauhausWatch Development Environment..."

# Create .devcontainer directory if it doesn't exist
mkdir -p .devcontainer

echo "Building development containers..."
docker-compose -f docker-compose.dev.yml build

echo "Starting development services..."
docker-compose -f docker-compose.dev.yml up -d

echo "Waiting for Elasticsearch to be ready..."
sleep 30

echo "Loading data into Elasticsearch..."
docker-compose -f docker-compose.dev.yml exec app python app/elasticsearch_loader.py

echo "Development environment is ready!"
echo ""
echo "To open in VS Code Dev Container:"
echo "1. Install the 'Dev Containers' extension in VS Code"
echo "2. Press Ctrl+Shift+P and run 'Dev Containers: Reopen in Container'"
echo "3. Or use the command palette: 'Dev Containers: Open Folder in Container'"
echo ""
echo "To run the application manually:"
echo "docker-compose -f docker-compose.dev.yml exec app python app.py"
echo ""
echo "To access Elasticsearch: http://localhost:9200"
echo "To access the app: http://localhost:8001" 