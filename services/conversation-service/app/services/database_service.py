"""
Database service for persistent conversation storage.
Supports SQLite (development) and PostgreSQL (production).
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./conversations.db")
USE_DATABASE = os.getenv("USE_DATABASE", "true").lower() == "true"

# Determine database type
DB_TYPE = "postgresql" if "postgresql" in DATABASE_URL else "sqlite"


class DatabaseService:
    """Service for persisting conversation data."""
    
    def __init__(self):
        self.db_type = DB_TYPE
        self.use_database = USE_DATABASE
        self.connection = None
        
        if self.use_database:
            self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection and create tables."""
        
        if self.db_type == "sqlite":
            self._initialize_sqlite()
        elif self.db_type == "postgresql":
            self._initialize_postgresql()
    
    def _initialize_sqlite(self):
        """Initialize SQLite database."""
        import sqlite3
        
        # Create database directory if needed
        db_path = DATABASE_URL.replace("sqlite:///", "")
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        
        # Create tables
        self._create_tables_sqlite()
        logger.info(f"SQLite database initialized at {db_path}")
    
    def _initialize_postgresql(self):
        """Initialize PostgreSQL database (requires psycopg2)."""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            self.connection = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
            self._create_tables_postgresql()
            logger.info("PostgreSQL database initialized")
        except ImportError:
            logger.error("psycopg2 not installed. Install with: pip install psycopg2-binary")
            self.use_database = False
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL: {e}")
            self.use_database = False
    
    def _create_tables_sqlite(self):
        """Create SQLite tables for conversation storage."""
        
        cursor = self.connection.cursor()
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                job_description TEXT,
                candidate_profile TEXT,
                interview_type TEXT,
                tone TEXT,
                status TEXT,
                current_topic TEXT,
                question_count INTEGER DEFAULT 0,
                start_time TEXT NOT NULL,
                end_time TEXT,
                last_activity TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                speaker TEXT,
                confidence REAL,
                metadata TEXT,
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON conversations(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversation ON messages(conversation_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)")
        
        self.connection.commit()
        logger.info("SQLite tables created successfully")
    
    def _create_tables_postgresql(self):
        """Create PostgreSQL tables for conversation storage."""
        
        cursor = self.connection.cursor()
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id VARCHAR(255) PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                job_description TEXT,
                candidate_profile JSONB,
                interview_type VARCHAR(50),
                tone VARCHAR(50),
                status VARCHAR(50),
                current_topic VARCHAR(100),
                question_count INTEGER DEFAULT 0,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                last_activity TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                conversation_id VARCHAR(255) NOT NULL,
                message_type VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                speaker VARCHAR(50),
                confidence REAL,
                metadata JSONB,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON conversations(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversation ON messages(conversation_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)")
        
        self.connection.commit()
        logger.info("PostgreSQL tables created successfully")
    
    def save_conversation(self, conversation: Dict[str, Any]) -> bool:
        """Save or update a conversation record."""
        
        if not self.use_database:
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Serialize complex fields
            candidate_profile = json.dumps(conversation.get("candidate_profile", {}))
            start_time = conversation["start_time"].isoformat() if isinstance(conversation["start_time"], datetime) else conversation["start_time"]
            end_time = conversation.get("end_time")
            if end_time and isinstance(end_time, datetime):
                end_time = end_time.isoformat()
            last_activity = conversation["last_activity"].isoformat() if isinstance(conversation["last_activity"], datetime) else conversation["last_activity"]
            
            if self.db_type == "sqlite":
                cursor.execute("""
                    INSERT OR REPLACE INTO conversations 
                    (conversation_id, session_id, job_description, candidate_profile, interview_type, 
                     tone, status, current_topic, question_count, start_time, end_time, last_activity, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    conversation["conversation_id"],
                    conversation["session_id"],
                    conversation.get("job_description"),
                    candidate_profile,
                    conversation.get("interview_type"),
                    conversation.get("tone"),
                    conversation.get("status"),
                    conversation.get("current_topic"),
                    conversation.get("question_count", 0),
                    start_time,
                    end_time,
                    last_activity
                ))
            else:  # PostgreSQL
                cursor.execute("""
                    INSERT INTO conversations 
                    (conversation_id, session_id, job_description, candidate_profile, interview_type, 
                     tone, status, current_topic, question_count, start_time, end_time, last_activity, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (conversation_id) DO UPDATE SET
                        status = EXCLUDED.status,
                        current_topic = EXCLUDED.current_topic,
                        question_count = EXCLUDED.question_count,
                        end_time = EXCLUDED.end_time,
                        last_activity = EXCLUDED.last_activity,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    conversation["conversation_id"],
                    conversation["session_id"],
                    conversation.get("job_description"),
                    candidate_profile,
                    conversation.get("interview_type"),
                    conversation.get("tone"),
                    conversation.get("status"),
                    conversation.get("current_topic"),
                    conversation.get("question_count", 0),
                    start_time,
                    end_time,
                    last_activity
                ))
            
            self.connection.commit()
            logger.debug(f"Saved conversation {conversation['conversation_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            self.connection.rollback()
            return False
    
    def save_message(
        self,
        conversation_id: str,
        message_type: str,
        content: str,
        speaker: str = "ai",
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """Save a message to the database."""
        
        if not self.use_database:
            return False
        
        try:
            cursor = self.connection.cursor()
            
            timestamp_str = (timestamp or datetime.now()).isoformat()
            metadata_json = json.dumps(metadata or {})
            
            if self.db_type == "sqlite":
                cursor.execute("""
                    INSERT INTO messages 
                    (conversation_id, message_type, content, speaker, confidence, metadata, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (conversation_id, message_type, content, speaker, confidence, metadata_json, timestamp_str))
            else:  # PostgreSQL
                cursor.execute("""
                    INSERT INTO messages 
                    (conversation_id, message_type, content, speaker, confidence, metadata, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (conversation_id, message_type, content, speaker, confidence, metadata_json, timestamp_str))
            
            self.connection.commit()
            logger.debug(f"Saved message for conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            self.connection.rollback()
            return False
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a conversation by ID."""
        
        if not self.use_database:
            return None
        
        try:
            cursor = self.connection.cursor()
            
            if self.db_type == "sqlite":
                cursor.execute("SELECT * FROM conversations WHERE conversation_id = ?", (conversation_id,))
            else:
                cursor.execute("SELECT * FROM conversations WHERE conversation_id = %s", (conversation_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving conversation: {e}")
            return None
    
    def get_messages(self, conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve messages for a conversation."""
        
        if not self.use_database:
            return []
        
        try:
            cursor = self.connection.cursor()
            
            if self.db_type == "sqlite":
                cursor.execute("""
                    SELECT * FROM messages 
                    WHERE conversation_id = ? 
                    ORDER BY timestamp ASC 
                    LIMIT ?
                """, (conversation_id, limit))
            else:
                cursor.execute("""
                    SELECT * FROM messages 
                    WHERE conversation_id = %s 
                    ORDER BY timestamp ASC 
                    LIMIT %s
                """, (conversation_id, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error retrieving messages: {e}")
            return []
    
    def get_conversation_by_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a conversation by session ID."""
        
        if not self.use_database:
            return None
        
        try:
            cursor = self.connection.cursor()
            
            if self.db_type == "sqlite":
                cursor.execute("SELECT * FROM conversations WHERE session_id = ? ORDER BY start_time DESC LIMIT 1", (session_id,))
            else:
                cursor.execute("SELECT * FROM conversations WHERE session_id = %s ORDER BY start_time DESC LIMIT 1", (session_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving conversation by session: {e}")
            return None
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")


# Global database service instance
database_service = DatabaseService()
