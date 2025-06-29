import json
import os
import time
import hashlib
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError
import pdfextract
import applog


def wait_for_elasticsearch(es, max_retries=30):
    """Wait for Elasticsearch to be ready"""
    for i in range(max_retries):
        try:
            if es.ping():
                applog.info("Elasticsearch is ready")
                return True
        except ConnectionError:
            pass
        applog.info(f"Waiting for Elasticsearch... ({i+1}/{max_retries})")
        time.sleep(2)
    return False


def create_index(es, index_name="protocols"):
    """Create the protocols index with proper mapping"""
    mapping = {
        "mappings": {
            "properties": {
                "title": {
                    "type": "text",
                    "analyzer": "german"
                },
                "committee": {
                    "type": "keyword"
                },
                "date": {
                    "type": "date",
                    "format": "dd.MM.yyyy"
                },
                "unixdate": {
                    "type": "long"
                },
                "content": {
                    "type": "text",
                    "analyzer": "german"
                },
                "url": {
                    "type": "keyword"
                },
                "local_url": {
                    "type": "keyword"
                },
                "filename": {
                    "type": "keyword"
                },
                "link_title": {
                    "type": "text",
                    "analyzer": "german"
                },
                "class": {
                    "type": "keyword"
                },
                "page": {
                    "type": "keyword"
                }
            }
        },
        "settings": {
            "analysis": {
                "analyzer": {
                    "german": {
                        "type": "german"
                    }
                }
            }
        }
    }
    
    try:
        es.indices.create(index=index_name, body=mapping)
        applog.info(f"Created index: {index_name}")
    except Exception as e:
        if "resource_already_exists_exception" in str(e):
            applog.info(f"Index {index_name} already exists")
        else:
            applog.error(f"Error creating index: {e}")
            raise

def extract_pdf_content(pdf_path):
    """Extract text content from PDF file"""
    try:
        if os.path.exists(pdf_path):
            # Use the correct function from pdfextract
            pages = pdfextract.get_text_from_pdf(pdf_path)
            # Combine all pages into one content string
            content = " ".join(pages.values())
            return content if content else ""
        else:
            applog.warning(f"PDF file not found: {pdf_path}")
            return ""
    except Exception as e:
        applog.error(f"Error extracting PDF content from {pdf_path}: {e}")
        return ""

def load_protocols_to_elasticsearch():
    """Load protocols from JSON and PDFs into Elasticsearch"""
    
    # Get Elasticsearch configuration
    es_host = os.environ.get('ELASTICSEARCH_HOST', 'localhost')
    es_port = os.environ.get('ELASTICSEARCH_PORT', '9200')
    
    # Connect to Elasticsearch
    es = Elasticsearch([f"http://{es_host}:{es_port}"])
    
    # Wait for Elasticsearch to be ready
    if not wait_for_elasticsearch(es):
        applog.error("Elasticsearch is not available")
        return False
    
    # Create index
    create_index(es)
    
    # Load protocols from JSON
    try:
        with open('app/protocols.json', 'r', encoding='utf-8') as f:
            protocols = json.load(f)
    except Exception as e:
        applog.error(f"Error loading protocols.json: {e}")
        return False
    
    applog.info(f"Loaded {len(protocols)} protocols from JSON")
    
    # Process each protocol
    indexed_count = 0
    skipped_count = 0
    
    for protocol in protocols:
        try:
            # Extract content from PDF if available
            pdf_path = protocol.get('local_url', '')
            if pdf_path:
                full_pdf_path = os.path.join('app', pdf_path)
                if os.path.exists(full_pdf_path):
                    # Generate file hash
                    with open(full_pdf_path, 'rb') as f:
                        file_bytes = f.read()
                        file_hash = hashlib.sha256(file_bytes).hexdigest()
                    
                    # Check if document with hash-0 already exists
                    doc_id = f"{file_hash}-0"
                    if es.exists(index='protocols', id=doc_id):
                        applog.info(f"Document with id {doc_id} already indexed, skipping file: {protocol.get('filename', 'unknown')}")
                        skipped_count += 1
                        continue
                    
                    # Extract all pages
                    pages = pdfextract.get_text_from_pdf(full_pdf_path)
                    for page_number, page_content in pages.items():
                        doc = {
                            'title': protocol.get('link_title', ''),
                            'class': protocol.get('class', ''),
                            'committee': protocol.get('committee', ''),
                            'date': protocol.get('date', ''),
                            'unixdate': protocol.get('unixdate', 0),
                            'content': page_content,
                            'url': protocol.get('url', ''),
                            'local_url': protocol.get('local_url', ''),
                            'filename': protocol.get('filename', ''),
                            'link_title': protocol.get('link_title', ''),
                            'page': page_number
                        }
                        if doc['date'] == 'Datum unbekannt' or not doc['date']:
                            doc['date'] = '01.01.1970'
                        
                        page_doc_id = f"{file_hash}-{page_number}"
                        es.index(index='protocols', id=page_doc_id, document=doc)
                        indexed_count += 1
                        
                        if indexed_count % 100 == 0:
                            applog.info(f"Indexed {indexed_count} protocol pages...")
                else:
                    applog.warning(f"PDF file not found: {full_pdf_path}")
            else:
                applog.warning(f"No PDF path for protocol: {protocol.get('filename', 'unknown')}")
                
        except Exception as e:
            applog.error(f"Error indexing protocol {protocol.get('filename', 'unknown')}: {e}")
            continue
    
    # Refresh index to make documents searchable
    es.indices.refresh(index='protocols')
    
    applog.info(f"Successfully indexed {indexed_count} protocol pages")
    applog.info(f"Skipped {skipped_count} files (already indexed)")
    return True

if __name__ == "__main__":
    applog.info("Starting Elasticsearch data loader...")
    success = load_protocols_to_elasticsearch()
    if success:
        applog.info("Elasticsearch data loading completed successfully")
    else:
        applog.error("Elasticsearch data loading failed")
        exit(1) 