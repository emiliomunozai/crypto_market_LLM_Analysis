import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class NewsItem(BaseModel):
    """A news item with its features."""
    date: datetime
    text: str
    source: str = "Crypto News"
    category: str = "Crypto"
    next_t_close: Optional[float] = None
    target: Optional[str] = None
    diff_perc: Optional[float] = None

class PriceData(BaseModel):
    """Price data point with extended fields."""
    date: datetime
    asset: str
    price: float
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None
    next_t_close: Optional[float] = None
    close_7: Optional[float] = None
    close_30: Optional[float] = None
    close_90: Optional[float] = None
    target: Optional[str] = None
    diff_perc: Optional[float] = None

class Fact(BaseModel):
    """A fact stored in long-term memory."""
    fact: str
    source: str
    confidence: float
    category: str
    timestamp: datetime = Field(default_factory=datetime.now)
    fact_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class Decision(BaseModel):
    """A decision made by the agent."""
    recommendation: str
    confidence: float
    reasoning: str
    timestamp: datetime = Field(default_factory=datetime.now)
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    outcome: Optional[str] = None
    reward: Optional[float] = None

class Consideration(BaseModel):
    """A consideration for future decisions."""
    text: str
    timestamp: datetime = Field(default_factory=datetime.now)
    consideration_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class Thought(BaseModel):
    """A thought in the agent's working memory."""
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    thought_id: str = Field(default_factory=lambda: str(uuid.uuid4()))