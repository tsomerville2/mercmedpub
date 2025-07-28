"""
Test data for BDD scenarios
"""

# Sample medical queries for testing
MEDICAL_QUERIES = [
    {
        "query": "COVID-19 vaccine efficacy in elderly populations",
        "expected_keywords": ["COVID-19", "vaccine", "efficacy", "elderly"],
        "filters": {
            "publication_date_start": "2021-01-01",
            "open_access": True
        }
    },
    {
        "query": "CRISPR-Cas9 applications in cancer treatment",
        "expected_keywords": ["CRISPR", "Cas9", "cancer", "treatment"],
        "filters": {
            "publication_date_start": "2020-01-01",
            "clinical_trials": True
        }
    },
    {
        "query": "Machine learning in drug discovery",
        "expected_keywords": ["machine learning", "drug discovery", "AI"],
        "filters": {
            "publication_date_start": "2019-01-01"
        }
    }
]

# Expected PubMed article structure
PUBMED_ARTICLE_SCHEMA = {
    "required_fields": [
        "pmid",
        "title",
        "abstract",
        "authors",
        "publication_date",
        "journal"
    ],
    "optional_fields": [
        "keywords",
        "mesh_terms",
        "doi",
        "pmc_id",
        "full_text_url"
    ]
}

# API response schemas
API_RESPONSE_SCHEMAS = {
    "query_response": {
        "query_id": "string",
        "status": "string",
        "results": {
            "articles": "array",
            "summary": "string",
            "total_count": "integer"
        },
        "metadata": {
            "processing_time": "float",
            "filters_applied": "object"
        }
    },
    "error_response": {
        "error": "string",
        "detail": "string",
        "status_code": "integer",
        "timestamp": "string"
    }
}

# Prefect workflow states
WORKFLOW_STATES = {
    "PENDING": "pending",
    "RUNNING": "running",
    "COMPLETED": "completed",
    "FAILED": "failed",
    "CANCELLED": "cancelled",
    "CACHED": "cached"
}

# Rate limit configurations
RATE_LIMITS = {
    "with_api_key": {
        "requests_per_second": 10,
        "burst_size": 20
    },
    "without_api_key": {
        "requests_per_second": 3,
        "burst_size": 5
    }
}