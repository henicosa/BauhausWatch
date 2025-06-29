#!/bin/bash

echo "Rebuilding BauhausWatch Dev Container..."

# Stop and remove existing containers
echo "Stopping existing containers..."
docker-compose -f docker-compose.dev.yml down

# Remove the dev container image to force a rebuild
echo "Removing existing dev container image..."
docker rmi bauhauswatch-dev 2>/dev/null || true

# Rebuild the dev container
echo "Rebuilding dev container..."
docker-compose -f docker-compose.dev.yml build --no-cache

# Start the dev container
echo "Starting dev container..."
docker-compose -f docker-compose.dev.yml up -d

echo "Dev container rebuild complete!"
echo "You can now open the project in VS Code and use 'Reopen in Container'"
echo "Or run: code . --remote-containers" 