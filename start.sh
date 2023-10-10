#!/bin/bash
docker run -p 5303:5000 -v "$(pwd)/app":/app/app --restart unless-stopped --name bauhausbot bauhausbot