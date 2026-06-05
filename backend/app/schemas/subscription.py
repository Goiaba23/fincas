from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SubscriptionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    amount: float = Field(gt=0)
    billing_cycle: str = Field(default="monthly", pattern="^(weekly|monthly|quarterly|yearly)$")
    category: str = Field(default="streaming")
    next_payment: Optional[str] = None


class SubscriptionUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    billing_cycle: Optional[str] = None
    category: Optional[str] = None
    next_payment: Optional[str] = None
    active: Optional[bool] = None


class SubscriptionResponse(BaseModel):
    id: str
    name: str
    amount: float
    billing_cycle: str
    category: str
    next_payment: Optional[datetime]
    active: bool
    monthly_cost: float


class SubscriptionAnalytics(BaseModel):
    total_monthly: float
    total_yearly: float
    subscription_count: int
    by_category: dict
    top_spending: list
