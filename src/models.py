from pydantic import BaseModel
from typing import Dict, Any, List, Optional
class Event(BaseModel):
    topic: str
    event_id: str
    timestamp: str
    source: str
    payload: Optional[Dict[str, Any]] = {}
class EventBatch(BaseModel):
    events: List[Event]
