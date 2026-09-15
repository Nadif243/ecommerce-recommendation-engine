import os
import sqlite3
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List

app = FastAPI(title="E-Commerce Recommendation API")
DB_PATH = os.path.join(os.path.dirname(__file__), "../data/clickstream.db")

# -----------------------------------------
# 1. Database Dependency
# -----------------------------------------
def get_db():
    """Opens a fresh database connection for each web request and closes it after."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# -----------------------------------------
# 2. Data Validation Schemas (Pydantic)
# -----------------------------------------
class EventPayload(BaseModel):
    user_id: int
    item_id: int
    event_type: str  # Must be 'view', 'cart', or 'buy'

class RecommendationResponse(BaseModel):
    item_id: int
    predicted_score: float
    rank: int

EVENT_WEIGHTS = {
    "view": 1.0,
    "cart": 3.0,
    "buy": 5.0
}

# -----------------------------------------
# 3. API Endpoints
# -----------------------------------------
@app.get("/api/v1/health")
def health_check():
    return {"status": "Hot Path API is running live."}

@app.post("/api/v1/events", status_code=201)
def log_event(event: EventPayload, db: sqlite3.Connection = Depends(get_db)):
    """Ingests real-time user clicks and writes them to the event log."""
    weight = EVENT_WEIGHTS.get(event.event_type)

    if weight is None:
        raise HTTPException(status_code=400, detail="Invalid event type. Must be 'view', 'cart', or 'buy'.")

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO events (user_id, item_id, event_type, weight)
        VALUES (?, ?, ?, ?)
    """, (event.user_id, event.item_id, event.event_type, weight))
    db.commit()

    return {"status": "success", "message": f"Logged {event.event_type} for User {event.user_id}"}

@app.get("/api/v1/recommendations/{user_id}", response_model=List[RecommendationResponse])
def get_recommendations(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Instantly serves pre-computed recommendations for a specific user."""
    cursor = db.cursor()
    cursor.execute("""
        SELECT item_id, predicted_score, rank
        FROM recommendations
        WHERE user_id = ?
        ORDER BY rank ASC
    """, (user_id,))

    rows = cursor.fetchall()

    # Handling the "Cold Start" problem for unknown users
    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"User not found or insufficient interaction history."
        )

    return [dict(row) for row in rows]
