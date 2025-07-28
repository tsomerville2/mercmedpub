# NCBI E-utilities API Guide

## Overview

The NCBI E-utilities (Entrez Programming Utilities) are a set of server-side programs that provide a stable interface to the Entrez query and database system at the National Center for Biotechnology Information (NCBI). This guide covers essential information for integrating with PubMed through E-utilities.

## API Rate Limits

### Without API Key
- **Limit**: 3 requests per second
- **Scope**: Per IP address
- **Error**: HTTP 429 if exceeded

### With API Key
- **Default Limit**: 10 requests per second
- **Scope**: Per API key (across all IPs using the key)
- **Higher Limits**: Available by request to vog.hin.mln.ibcn@seitilitue

### Important Notes
- Rate limits apply to request initiation, not completion
- Multiple concurrent requests are allowed as long as initiation rate is respected
- Limits apply to all E-utilities combined (ESearch, EFetch, ESummary, etc.)

## Getting an API Key

1. Create an NCBI account at https://www.ncbi.nlm.nih.gov/account/
2. Navigate to Account Settings
3. Find "API Key Management" section
4. Click "Create an API Key"
5. Copy and securely store your key

**Usage Example**:
```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=cancer&api_key=YOUR_KEY_HERE
```

## Core E-utilities

### 1. EInfo - Database Information
Provides information about NCBI databases.

**Endpoint**: `/entrez/eutils/einfo.fcgi`

**Example**:
```bash
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=pubmed&api_key=YOUR_KEY"
```

### 2. ESearch - Search Database
Searches and retrieves primary IDs.

**Endpoint**: `/entrez/eutils/esearch.fcgi`

**Parameters**:
- `db`: Database name (e.g., "pubmed")
- `term`: Search query
- `retmax`: Maximum number of IDs to return (default: 20, max: 10,000)
- `retstart`: Sequential index of first ID to retrieve
- `sort`: Sort order (relevance, pub_date, Author, etc.)
- `datetype`: Date field to search (pdat, edat, mdat)
- `mindate`, `maxdate`: Date range limits

**Example**:
```bash
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=COVID-19+vaccine&retmax=100&sort=pub_date&api_key=YOUR_KEY"
```

### 3. ESummary - Document Summary
Retrieves document summaries for a list of IDs.

**Endpoint**: `/entrez/eutils/esummary.fcgi`

**Parameters**:
- `db`: Database name
- `id`: Comma-delimited list of IDs
- `retmode`: xml (default) or json

**Example**:
```bash
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=34662886,34662885&retmode=json&api_key=YOUR_KEY"
```

### 4. EFetch - Retrieve Full Records
Retrieves full records in various formats.

**Endpoint**: `/entrez/eutils/efetch.fcgi`

**Parameters**:
- `db`: Database name
- `id`: Comma-delimited list of IDs
- `rettype`: Return type (abstract, medline, xml, etc.)
- `retmode`: Return mode (text, xml, asn.1)

**Example**:
```bash
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=34662886&rettype=abstract&retmode=text&api_key=YOUR_KEY"
```

### 5. ELink - Find Related Data
Retrieves IDs of related or linked records.

**Endpoint**: `/entrez/eutils/elink.fcgi`

**Parameters**:
- `dbfrom`: Source database
- `db`: Destination database
- `id`: Source ID(s)
- `linkname`: Specific link to retrieve

**Example**:
```bash
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&db=pmc&id=34662886&api_key=YOUR_KEY"
```

## Best Practices

### 1. Efficient Searching
```python
# Good: Use specific field tags
query = "Fauci A[Author] AND COVID-19[Title]"

# Better: Add date constraints
query = "Fauci A[Author] AND COVID-19[Title] AND 2020:2023[pdat]"

# Best: Use MeSH terms for precision
query = "COVID-19[MeSH] AND vaccines[MeSH Major Topic]"
```

### 2. Pagination for Large Result Sets
```python
def fetch_all_results(query, api_key):
    results = []
    retstart = 0
    retmax = 500  # Fetch in batches
    
    while True:
        response = esearch(
            db="pubmed",
            term=query,
            retstart=retstart,
            retmax=retmax,
            api_key=api_key
        )
        
        ids = response['idlist']
        results.extend(ids)
        
        if len(ids) < retmax:
            break
            
        retstart += retmax
        time.sleep(0.1)  # Rate limiting
    
    return results
```

### 3. Error Handling
```python
import time
import requests
from urllib.parse import urlencode

def make_request_with_retry(url, params, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 429:
                # Rate limit exceeded
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
                continue
                
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(1)
    
    return None
```

### 4. Combining E-utilities
```python
def get_full_articles(query, api_key, max_results=10):
    # Step 1: Search for articles
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        'db': 'pubmed',
        'term': query,
        'retmax': max_results,
        'api_key': api_key,
        'retmode': 'json'
    }
    
    search_response = requests.get(search_url, params=search_params).json()
    pmids = search_response['esearchresult']['idlist']
    
    # Step 2: Fetch summaries
    summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    summary_params = {
        'db': 'pubmed',
        'id': ','.join(pmids),
        'api_key': api_key,
        'retmode': 'json'
    }
    
    summary_response = requests.get(summary_url, params=summary_params).json()
    
    # Step 3: Fetch full abstracts if needed
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    articles = []
    
    for pmid in pmids:
        fetch_params = {
            'db': 'pubmed',
            'id': pmid,
            'rettype': 'abstract',
            'retmode': 'xml',
            'api_key': api_key
        }
        
        abstract_response = requests.get(fetch_url, params=fetch_params)
        articles.append({
            'pmid': pmid,
            'summary': summary_response['result'][pmid],
            'abstract': abstract_response.text
        })
        
        time.sleep(0.1)  # Rate limiting
    
    return articles
```

## Search Query Syntax

### Field Tags
- `[Author]` - Author name
- `[Title]` - Article title
- `[Title/Abstract]` - Title or abstract
- `[MeSH]` - MeSH terms
- `[MeSH Major Topic]` - MeSH major topics
- `[Journal]` - Journal name
- `[pdat]` - Publication date
- `[Filter]` - Predefined filters

### Boolean Operators
- `AND` - Both terms must be present
- `OR` - Either term can be present
- `NOT` - Exclude term
- Use parentheses for grouping

### Date Ranges
- `2020[pdat]` - Published in 2020
- `2020:2023[pdat]` - Published between 2020-2023
- `2020/01/01:2020/12/31[pdat]` - Specific date range

### Examples
```
# Complex query with multiple criteria
"machine learning"[Title/Abstract] AND cancer[MeSH] AND 2020:2023[pdat] AND "clinical trial"[Publication Type]

# Author-specific search
"Smith J"[Author] AND Harvard[Affiliation]

# Open access articles only
"COVID-19"[Title] AND "open access"[filter]
```

## Common Error Codes

| Error Code | Description | Solution |
|------------|-------------|----------|
| 429 | Rate limit exceeded | Add API key or reduce request rate |
| 400 | Bad request | Check query syntax and parameters |
| 404 | ID not found | Verify PMID exists |
| 500 | Server error | Retry with exponential backoff |

## Limitations

1. **Search Results**: Maximum 10,000 PMIDs per search
2. **Batch Size**: Recommended max 200 IDs per ESummary/EFetch request
3. **Query Length**: URLs should not exceed 2048 characters
4. **Date Ranges**: Some databases have limited date range support

## Tips for Production Use

1. **Implement Caching**: Cache frequently accessed data to reduce API calls
2. **Use POST for Large Queries**: For queries with many IDs, use HTTP POST
3. **Monitor Usage**: Track your API usage to avoid hitting limits
4. **Schedule Large Jobs**: Run intensive operations during off-peak hours (9 PM - 5 AM EST)
5. **Handle Network Issues**: Implement robust retry logic with exponential backoff

## Additional Resources

- [E-utilities Quick Start](https://www.ncbi.nlm.nih.gov/books/NBK25500/)
- [E-utilities In-Depth](https://www.ncbi.nlm.nih.gov/books/NBK25499/)
- [PubMed Help](https://pubmed.ncbi.nlm.nih.gov/help/)
- [NCBI Support](https://support.nlm.nih.gov/)