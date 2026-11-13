"""Schemas para Subscription Tracker."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str = "#6366f1"


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = None


class CategoryOut(CategoryCreate):
    id: int
    subscription_count: int = 0


class SubscriptionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    frequency: str = Field(..., pattern="^(monthly|yearly)$")
    category_id: int
    next_due_date: date
    description: Optional[str] = None
    website: Optional[str] = None


class SubscriptionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    frequency: Optional[str] = None
    category_id: Optional[int] = None
    next_due_date: Optional[date] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SubscriptionOut(BaseModel):
    id: int
    name: str
    price: float
    frequency: str
    category_id: int
    category_name: Optional[str] = None
    category_color: Optional[str] = None
    next_due_date: date
    description: Optional[str] = None
    website: Optional[str] = None
    is_active: bool
    days_until_due: Optional[int] = None
    created_at: str


class DashboardStats(BaseModel):
    total_monthly_spending: float
    total_yearly_spending: float
    upcoming_renewals: list[dict]
    top_category: Optional[str]
    top_category_spending: float
    active_subscriptions: int
    total_subscriptions: int
