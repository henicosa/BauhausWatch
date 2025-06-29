#!/bin/bash

echo "=== Elasticsearch Health Check ==="
curl -s http://localhost:9200/_cluster/health | jq . 2>/dev/null || echo "Elasticsearch not accessible"

echo -e "\n=== Protocols Index Status ==="
curl -s http://localhost:9200/protocols/_count | jq . 2>/dev/null || echo "Protocols index not found"

echo -e "\n=== Sample Search Test ==="
curl -s -X POST "http://localhost:9200/protocols/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "match": {
        "committee": "Senat"
      }
    },
    "size": 1
  }' | jq '.hits.total.value' 2>/dev/null || echo "Search test failed"

echo -e "\n=== Container Status ==="
docker-compose ps 