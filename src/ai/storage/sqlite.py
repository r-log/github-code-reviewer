import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

import aiosqlite

from .base import StorageProvider, ReviewRecord
from ..models.response import AIResponse
from ..models.request import ReviewType
from ..exceptions import StorageError


class SQLiteStorage(StorageProvider):
    """SQLite-based storage provider for review history."""

    def __init__(self, db_path: str = "reviews.db"):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        """Ensure database and tables exist."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    review_type TEXT NOT NULL,
                    review_response TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    metadata TEXT
                )
            """)
            # Create indices for common queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_reviews_file_path
                ON reviews(file_path)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_reviews_timestamp
                ON reviews(timestamp)
            """)
            conn.commit()
        finally:
            conn.close()

    def _serialize_review(self, review: AIResponse) -> str:
        """Serialize review response to JSON."""
        return json.dumps({
            "comments": [
                {
                    "line_number": c.line_number,
                    "content": c.content,
                    "severity": c.severity,
                    "category": c.category,
                    "suggested_fix": c.suggested_fix
                }
                for c in review.comments
            ],
            "summary": review.summary,
            "score": review.score,
            "metadata": review.metadata
        })

    def _deserialize_review(self, data: str) -> AIResponse:
        """Deserialize review response from JSON."""
        try:
            review_data = json.loads(data)
            from ..models.response import ReviewComment

            comments = [
                ReviewComment(
                    line_number=c["line_number"],
                    content=c["content"],
                    severity=c["severity"],
                    category=c["category"],
                    suggested_fix=c.get("suggested_fix")
                )
                for c in review_data["comments"]
            ]

            return AIResponse(
                comments=comments,
                summary=review_data["summary"],
                score=review_data.get("score"),
                metadata=review_data.get("metadata")
            )
        except (json.JSONDecodeError, KeyError) as e:
            raise StorageError(f"Failed to deserialize review: {str(e)}")

    async def save_review(
        self,
        file_path: str,
        review_type: ReviewType,
        review: AIResponse,
        metadata: Optional[Dict] = None
    ) -> str:
        """Save a review and return its ID."""
        review_id = str(uuid.uuid4())
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO reviews (id, file_path, review_type, review_response, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        review_id,
                        file_path,
                        review_type.value,
                        self._serialize_review(review),
                        datetime.utcnow().isoformat(),
                        json.dumps(metadata) if metadata else None
                    )
                )
                await db.commit()
            return review_id
        except Exception as e:
            raise StorageError(f"Failed to save review: {str(e)}")

    async def get_review(self, review_id: str) -> Optional[ReviewRecord]:
        """Get a review by its ID."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT * FROM reviews WHERE id = ?",
                    (review_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        return None

                    return ReviewRecord(
                        id=row[0],
                        file_path=row[1],
                        review_type=ReviewType(row[2]),
                        review_response=self._deserialize_review(row[3]),
                        timestamp=datetime.fromisoformat(row[4]),
                        metadata=json.loads(row[5]) if row[5] else None
                    )
        except Exception as e:
            raise StorageError(f"Failed to get review: {str(e)}")

    async def get_file_reviews(
        self,
        file_path: str,
        limit: Optional[int] = None,
        review_type: Optional[ReviewType] = None
    ) -> List[ReviewRecord]:
        """Get review history for a file."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                query = "SELECT * FROM reviews WHERE file_path = ?"
                params = [file_path]

                if review_type:
                    query += " AND review_type = ?"
                    params.append(review_type.value)

                query += " ORDER BY timestamp DESC"
                if limit:
                    query += f" LIMIT {limit}"

                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    return [
                        ReviewRecord(
                            id=row[0],
                            file_path=row[1],
                            review_type=ReviewType(row[2]),
                            review_response=self._deserialize_review(row[3]),
                            timestamp=datetime.fromisoformat(row[4]),
                            metadata=json.loads(row[5]) if row[5] else None
                        )
                        for row in rows
                    ]
        except Exception as e:
            raise StorageError(f"Failed to get file reviews: {str(e)}")

    async def get_reviews_in_timeframe(
        self,
        start_time: datetime,
        end_time: datetime,
        review_type: Optional[ReviewType] = None
    ) -> List[ReviewRecord]:
        """Get reviews within a timeframe."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                query = "SELECT * FROM reviews WHERE timestamp BETWEEN ? AND ?"
                params = [start_time.isoformat(), end_time.isoformat()]

                if review_type:
                    query += " AND review_type = ?"
                    params.append(review_type.value)

                query += " ORDER BY timestamp DESC"

                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    return [
                        ReviewRecord(
                            id=row[0],
                            file_path=row[1],
                            review_type=ReviewType(row[2]),
                            review_response=self._deserialize_review(row[3]),
                            timestamp=datetime.fromisoformat(row[4]),
                            metadata=json.loads(row[5]) if row[5] else None
                        )
                        for row in rows
                    ]
        except Exception as e:
            raise StorageError(f"Failed to get reviews in timeframe: {str(e)}")

    async def delete_review(self, review_id: str) -> bool:
        """Delete a review by its ID."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "DELETE FROM reviews WHERE id = ?",
                    (review_id,)
                )
                await db.commit()
                return cursor.rowcount > 0
        except Exception as e:
            raise StorageError(f"Failed to delete review: {str(e)}")

    async def cleanup_old_reviews(self, older_than: datetime) -> int:
        """Delete reviews older than specified datetime."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "DELETE FROM reviews WHERE timestamp < ?",
                    (older_than.isoformat(),)
                )
                await db.commit()
                return cursor.rowcount
        except Exception as e:
            raise StorageError(f"Failed to cleanup old reviews: {str(e)}")
