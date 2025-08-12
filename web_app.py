"""Minimal Flask web application for viewing log events.

The application expects an Elasticsearch instance and exposes a single
endpoint for listing collected monitoring events.
"""

import os
from flask import Flask, jsonify

try:
    from elasticsearch import Elasticsearch  # type: ignore
except ImportError:  # pragma: no cover
    Elasticsearch = None  # type: ignore

app = Flask(__name__)

if Elasticsearch:
    es = Elasticsearch(os.getenv("ELASTIC_HOST", "http://localhost:9200"))
else:  # pragma: no cover
    es = None


@app.get("/logs")
def list_logs():
    """Return log documents stored in Elasticsearch."""
    if not es:
        return jsonify({"error": "Elasticsearch client not configured"}), 500
    resp = es.search(index="monitoring", query={"match_all": {}})
    hits = [hit.get("_source", {}) for hit in resp.get("hits", {}).get("hits", [])]
    return jsonify(hits)


if __name__ == "__main__":
    app.run(debug=True)
