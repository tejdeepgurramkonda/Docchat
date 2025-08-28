"""
Database module for ChatDocs AI
Handles persistent storage of chats, messages, and documents
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    """SQLite database handler for ChatDocs AI"""
    
    def __init__(self, db_path: str = "data/docchat.db"):
        self.db_path = db_path
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS chats (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        document_filename TEXT,
                        document_path TEXT,
                        chunks_count INTEGER DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages (chat_id)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_chats_created_at ON chats (created_at)
                """)
                
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def create_chat(self, chat_id: str, title: str, document_filename: str = None, 
                   document_path: str = None, chunks_count: int = 0) -> bool:
        """Create a new chat"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO chats (id, title, document_filename, document_path, chunks_count)
                    VALUES (?, ?, ?, ?, ?)
                """, (chat_id, title, document_filename, document_path, chunks_count))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error creating chat {chat_id}: {e}")
            return False
    
    def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get chat by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM chats WHERE id = ?
                """, (chat_id,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            logger.error(f"Error getting chat {chat_id}: {e}")
            return None
    
    def get_all_chats(self) -> List[Dict[str, Any]]:
        """Get all chats ordered by creation date (newest first)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT *, 
                           (SELECT COUNT(*) FROM messages WHERE chat_id = chats.id) as message_count
                    FROM chats 
                    ORDER BY created_at DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all chats: {e}")
            return []
    
    def update_chat_title(self, chat_id: str, title: str) -> bool:
        """Update chat title"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE chats SET title = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (title, chat_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating chat title {chat_id}: {e}")
            return False
    
    def delete_chat(self, chat_id: str) -> bool:
        """Delete chat and all its messages"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Delete messages first (foreign key constraint)
                conn.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
                # Delete chat
                conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting chat {chat_id}: {e}")
            return False
    
    def add_message(self, chat_id: str, role: str, content: str) -> bool:
        """Add a message to a chat"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO messages (chat_id, role, content)
                    VALUES (?, ?, ?)
                """, (chat_id, role, content))
                
                # Update chat's updated_at timestamp
                conn.execute("""
                    UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE id = ?
                """, (chat_id,))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding message to chat {chat_id}: {e}")
            return False
    
    def get_chat_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a chat"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM messages 
                    WHERE chat_id = ? 
                    ORDER BY timestamp ASC
                """, (chat_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting messages for chat {chat_id}: {e}")
            return []
    
    def get_chat_with_messages(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get chat with all its messages"""
        chat = self.get_chat(chat_id)
        if not chat:
            return None
        
        messages = self.get_chat_messages(chat_id)
        chat['messages'] = messages
        return chat
    
    def chat_exists(self, chat_id: str) -> bool:
        """Check if chat exists"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT 1 FROM chats WHERE id = ?", (chat_id,))
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking if chat exists {chat_id}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get chat count
                cursor = conn.execute("SELECT COUNT(*) FROM chats")
                chat_count = cursor.fetchone()[0]
                
                # Get message count
                cursor = conn.execute("SELECT COUNT(*) FROM messages")
                message_count = cursor.fetchone()[0]
                
                # Get most recent chat
                cursor = conn.execute("SELECT created_at FROM chats ORDER BY created_at DESC LIMIT 1")
                row = cursor.fetchone()
                last_chat_date = row[0] if row else None
                
                return {
                    "total_chats": chat_count,
                    "total_messages": message_count,
                    "last_chat_date": last_chat_date,
                    "database_path": self.db_path
                }
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def cleanup_old_chats(self, days_old: int = 30) -> int:
        """Delete chats older than specified days (for maintenance)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM chats 
                    WHERE created_at < datetime('now', '-{} days')
                """.format(days_old))
                deleted_count = cursor.rowcount
                conn.commit()
                logger.info(f"Cleaned up {deleted_count} old chats")
                return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up old chats: {e}")
            return 0

# Singleton database instance
db = Database()
