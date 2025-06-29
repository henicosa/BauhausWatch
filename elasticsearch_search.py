import os
from elasticsearch import Elasticsearch
from collections import defaultdict
from datetime import datetime

def search_with_elasticsearch(query):
    """Search using Elasticsearch and aggregate results by protocol."""
    # Get Elasticsearch configuration from environment
    es_host = os.environ.get('ELASTICSEARCH_HOST', 'localhost')
    es_port = os.environ.get('ELASTICSEARCH_PORT', '9200')
    index = os.environ.get('ELASTICSEARCH_INDEX', 'protocols')
    
    es = Elasticsearch([f"http://{es_host}:{es_port}"])
    
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
            },
            "fragment_size": 120,
            "number_of_fragments": 3
        },
        "size": 100
    }
    
    response = es.search(index=index, body=search_body)
    grouped = defaultdict(lambda: {
        "url": None,
        "class": None,
        "committee": None,
        "date": None,
        "matches": []
    })
    for hit in response['hits']['hits']:
        src = hit['_source']
        # Use highlights if available, else fallback to content
        snippets = []
        if 'highlight' in hit and 'content' in hit['highlight']:
            snippets = hit['highlight']['content']
        else:
            # fallback: show the first 120 chars
            snippets = [src.get('content', '')[:120]]
        for snippet in snippets:
            # Replace <em> tags with <span class="es-highlight">
            snippet = snippet.replace('<em>', '<span class="es-highlight">').replace('</em>', '</span>')
            match = {
                "page": src.get('page', None),
                "position": None,  # Not available from ES
                "snippet": snippet,
                "match_url": f"{src.get('url', '')}#page={src.get('page', '')}&search={query}"
            }
            key = (src.get('url', ''), src.get('committee', ''), src.get('date', ''))
            group = grouped[key]
            group["url"] = src.get('url', '')
            group["class"] = src.get('class', '') if 'class' in src else ''
            group["committee"] = src.get('committee', '')
            group["date"] = src.get('date', '')
            group["matches"].append(match)
    # Convert to list and sort by date descending
    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, "%d.%m.%Y")
        except Exception:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except Exception:
                return datetime.min
    results = list(grouped.values())
    # Sort matches by page ascending for each protocol
    for group in results:
        group["matches"].sort(key=lambda m: (m["page"] if m["page"] is not None else 0))
    results.sort(key=lambda x: parse_date(x["date"]), reverse=True)
    return results 