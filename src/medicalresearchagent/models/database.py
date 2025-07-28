"""Database models and setup for Medical Research Agent"""

import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)

Base = declarative_base()


class ResearchQuery(Base):
    """Store research queries submitted by users"""
    __tablename__ = 'research_queries'
    
    id = Column(String, primary_key=True)  # UUID
    query_text = Column(Text, nullable=False)
    filters = Column(JSON, nullable=True)  # Store filter parameters as JSON
    status = Column(String, default='pending')  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    processing_time = Column(Float, nullable=True)  # seconds
    user_id = Column(String, nullable=True)  # For future user management
    
    # Results
    article_count = Column(Integer, default=0)
    summary = Column(Text, nullable=True)  # AI-generated summary
    error_message = Column(Text, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'query_id': self.id,
            'query': self.query_text,
            'filters': self.filters or {},
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'processing_time': self.processing_time,
            'article_count': self.article_count,
            'summary': self.summary,
            'error': self.error_message
        }


class Article(Base):
    """Store article metadata from PubMed"""
    __tablename__ = 'articles'
    
    pmid = Column(String, primary_key=True)
    query_id = Column(String, nullable=False)  # Link to ResearchQuery
    title = Column(Text, nullable=False)
    authors = Column(JSON)  # List of author names
    abstract = Column(Text, nullable=True)
    publication_date = Column(String, nullable=True)
    journal = Column(String, nullable=True)
    doi = Column(String, nullable=True)
    keywords = Column(JSON)  # List of keywords
    mesh_terms = Column(JSON)  # List of MeSH terms
    
    # Metadata
    retrieved_at = Column(DateTime, default=datetime.utcnow)
    relevance_score = Column(Float, nullable=True)  # For future ML ranking
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'pmid': self.pmid,
            'title': self.title,
            'authors': self.authors or [],
            'abstract': self.abstract,
            'publication_date': self.publication_date,
            'journal': self.journal,
            'doi': self.doi,
            'keywords': self.keywords or [],
            'mesh_terms': self.mesh_terms or []
        }


class DatabaseManager:
    """Manage database connections and operations"""
    
    def __init__(self, database_url: Optional[str] = None):
        if not database_url:
            # Default to SQLite in the project directory
            db_path = os.path.join(os.path.dirname(__file__), '../../..', 'medical_research.db')
            database_url = f'sqlite:///{os.path.abspath(db_path)}'
        
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    def save_query(self, query_data: Dict[str, Any]) -> ResearchQuery:
        """Save a new research query"""
        session = self.get_session()
        try:
            query = ResearchQuery(**query_data)
            session.add(query)
            session.commit()
            session.refresh(query)
            return query
        finally:
            session.close()
    
    def update_query(self, query_id: str, **kwargs) -> Optional[ResearchQuery]:
        """Update an existing query"""
        session = self.get_session()
        try:
            query = session.query(ResearchQuery).filter_by(id=query_id).first()
            if query:
                for key, value in kwargs.items():
                    setattr(query, key, value)
                session.commit()
                session.refresh(query)
            return query
        finally:
            session.close()
    
    def get_query(self, query_id: str) -> Optional[ResearchQuery]:
        """Get a query by ID"""
        session = self.get_session()
        try:
            return session.query(ResearchQuery).filter_by(id=query_id).first()
        finally:
            session.close()
    
    def save_articles(self, query_id: str, articles: List[Dict[str, Any]]) -> int:
        """Save articles for a query"""
        session = self.get_session()
        try:
            saved_count = 0
            for article_data in articles:
                # Check if article already exists
                existing = session.query(Article).filter_by(pmid=article_data['pmid']).first()
                if not existing:
                    # Remove query_id from article_data if it exists to avoid duplicate
                    article_data_copy = article_data.copy()
                    article_data_copy.pop('query_id', None)
                    
                    article = Article(
                        query_id=query_id,
                        **article_data_copy
                    )
                    session.add(article)
                    saved_count += 1
            
            session.commit()
            return saved_count
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving articles: {e}")
            raise
        finally:
            session.close()
    
    def get_articles(self, query_id: str) -> List[Article]:
        """Get all articles for a query"""
        session = self.get_session()
        try:
            return session.query(Article).filter_by(query_id=query_id).all()
        finally:
            session.close()


# Global database manager instance
db_manager = DatabaseManager()