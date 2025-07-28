#!/usr/bin/env python3
"""Quick API test to demonstrate functionality"""

import requests
import json
import time

# Test the API
print("Testing Medical Research Agent API...\n")

# 1. Health check
print("1. Health Check:")
response = requests.get("http://localhost:8000/health")
if response.status_code == 200:
    print("   ✅ API is healthy")
    print(f"   Response: {response.json()}")
else:
    print("   ❌ API is not running. Start with: python play.py")
    exit(1)

# 2. Submit a research query
print("\n2. Submitting Research Query:")
query_data = {
    "query": "Latest CAR-T cell therapy for leukemia 2023",
    "filters": {
        "publication_date_start": "2023-01-01",
        "open_access": True,
        "maxResults": 10
    }
}

print(f"   Query: {query_data['query']}")
print(f"   Filters: {query_data['filters']}")

response = requests.post(
    "http://localhost:8000/api/query",
    json=query_data
)

if response.status_code == 200:
    result = response.json()
    print("   ✅ Query submitted successfully")
    print(f"   Query ID: {result['query_id']}")
    print(f"   Status: {result['status']}")
    print(f"   Articles found: {result.get('article_count', 'N/A')}")
    
    if result.get('summary'):
        print("\n3. AI Analysis Summary:")
        print("   " + result['summary'].replace('\n', '\n   '))
    
    # Get articles
    if result['status'] == 'completed' and result.get('query_id'):
        print("\n4. Sample Articles:")
        articles_response = requests.get(
            f"http://localhost:8000/api/query/{result['query_id']}/articles"
        )
        if articles_response.status_code == 200:
            articles_data = articles_response.json()
            articles = articles_data.get('articles', [])
            for i, article in enumerate(articles[:3], 1):
                print(f"\n   Article {i}:")
                print(f"   Title: {article['title']}")
                print(f"   Authors: {', '.join(article.get('authors', [])[:3])}...")
                print(f"   PMID: {article['pmid']}")
                print(f"   Date: {article.get('publication_date', 'N/A')}")
else:
    print(f"   ❌ Error: {response.status_code}")
    print(f"   Details: {response.text}")

print("\n✨ Test complete!")
