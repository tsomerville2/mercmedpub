"""FastAPI application for Medical Research Agent"""

import os
import uuid
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..workflow.simple_flow import medical_research_flow_simple
from ..models.database import db_manager

# FastAPI app
app = FastAPI(
    title="Medical Research Agent API",
    description="API for querying PubMed medical literature with AI analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str = Field(..., description="Research query in natural language")
    filters: Optional[Dict[str, Any]] = Field(default={}, description="Optional filters")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "Latest treatments for Type 2 Diabetes",
                "filters": {
                    "publication_date_start": "2022-01-01",
                    "open_access": True
                }
            }
        }
    }


class QueryResponse(BaseModel):
    query_id: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    processing_time: Optional[float] = None
    article_count: Optional[int] = None
    summary: Optional[str] = None
    error: Optional[str] = None


class BatchQueryRequest(BaseModel):
    queries: List[QueryRequest]


class BatchQueryResponse(BaseModel):
    results: List[QueryResponse]


# Dependency for API key validation
async def verify_api_key(authorization: Optional[str] = Header(None)) -> bool:
    """Verify API key for authentication"""
    if not authorization:
        # For MVP, allow without auth
        return True
    
    expected_key = os.getenv("TEST_API_KEY", "test-api-key-for-development")
    if authorization == f"Bearer {expected_key}":
        return True
    
    raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Medical Research Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/api/query", response_model=QueryResponse)
async def submit_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    authenticated: bool = Depends(verify_api_key)
) -> QueryResponse:
    """Submit a research query for processing"""
    
    # Generate query ID
    query_id = str(uuid.uuid4())
    
    try:
        # Run the workflow synchronously for MVP
        result = await medical_research_flow_simple(
            query_text=request.query,
            filters=request.filters,
            query_id=query_id,
            api_key=os.getenv("NCBI_API_KEY")
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        # Return error response
        return QueryResponse(
            query_id=query_id,
            status="failed",
            created_at=datetime.utcnow().isoformat(),
            error=str(e)
        )


@app.post("/api/query/async", response_model=QueryResponse)
async def submit_query_async(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    authenticated: bool = Depends(verify_api_key)
) -> QueryResponse:
    """Submit a research query for asynchronous processing"""
    
    # Generate query ID
    query_id = str(uuid.uuid4())
    
    # Add to background tasks
    background_tasks.add_task(
        medical_research_flow_simple,
        query_text=request.query,
        filters=request.filters,
        query_id=query_id,
        api_key=os.getenv("NCBI_API_KEY")
    )
    
    # Return immediate response
    return QueryResponse(
        query_id=query_id,
        status="processing",
        created_at=datetime.utcnow().isoformat()
    )


@app.get("/api/query/status/{query_id}", response_model=QueryResponse)
async def get_query_status(
    query_id: str,
    authenticated: bool = Depends(verify_api_key)
) -> QueryResponse:
    """Get the status of a submitted query"""
    
    query = db_manager.get_query(query_id)
    
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    
    return QueryResponse(**query.to_dict())


@app.get("/api/query/{query_id}/articles")
async def get_query_articles(
    query_id: str,
    authenticated: bool = Depends(verify_api_key)
) -> Dict[str, Any]:
    """Get articles for a completed query"""
    
    query = db_manager.get_query(query_id)
    
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    
    if query.status != "completed":
        return {
            "query_id": query_id,
            "status": query.status,
            "articles": []
        }
    
    articles = db_manager.get_articles(query_id)
    
    return {
        "query_id": query_id,
        "status": "completed",
        "article_count": len(articles),
        "articles": [article.to_dict() for article in articles]
    }


@app.post("/api/query/batch", response_model=BatchQueryResponse)
async def submit_batch_queries(
    request: BatchQueryRequest,
    background_tasks: BackgroundTasks,
    authenticated: bool = Depends(verify_api_key)
) -> BatchQueryResponse:
    """Submit multiple queries for processing"""
    
    results = []
    
    for query_req in request.queries:
        query_id = str(uuid.uuid4())
        
        try:
            # Run each query
            result = await medical_research_flow_simple(
                query_text=query_req.query,
                filters=query_req.filters,
                query_id=query_id,
                api_key=os.getenv("NCBI_API_KEY")
            )
            
            results.append(QueryResponse(**result))
            
        except Exception as e:
            results.append(QueryResponse(
                query_id=query_id,
                status="failed",
                created_at=datetime.utcnow().isoformat(),
                error=str(e)
            ))
    
    return BatchQueryResponse(results=results)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


# Error handlers
@app.exception_handler(422)
async def validation_exception_handler(request, exc):
    """Handle validation errors"""
    return {
        "error": "Validation Error",
        "detail": exc.errors(),
        "status_code": 422,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle internal server errors"""
    return {
        "error": "Internal Server Error",
        "detail": "An unexpected error occurred",
        "status_code": 500,
        "timestamp": datetime.utcnow().isoformat()
    }