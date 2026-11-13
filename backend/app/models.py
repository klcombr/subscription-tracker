"""Models para o Subscription Tracker - banco SQLite com tabelas de assinaturas e categorias."""

import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


# --- Pydantic Models ---

class CategoryBase(BaseModel):
    name: str
    color: str = "#6366f1"  # cor hex para UI


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    id: int
    subscription_count: int = 0

    model_config = {"from_attributes": True}


class SubscriptionBase(BaseModel):
    name: str
    price: float = Field(..., gt=0)
    frequency: str = Field(..., pattern="^(monthly|yearly)$")
    category_id: int
    next_due_date: date
    description: Optional[str] = None
    website: Optional[str] = None


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    frequency: Optional[str] = None
    category_id: Optional[int] = None
    next_due_date: Optional[date] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SubscriptionOut(SubscriptionBase):
    id: int
    category_name: Optional[str] = None
    category_color: Optional[str] = None
    is_active: bool
    days_until_due: Optional[int] = None
    created_at: str

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    total_monthly_spending: float
    total_yearly_spending: float
    upcoming_renewals: list  # ass.instruções próximas do vencimento
    top_category: Optional[str] = None
    top_category_spending: float = 0.0
    active_subscriptions: int
    total_subscriptions: int


# --- Database Layer ---

DB_PATH = Path(__file__).parent.parent / "subscriptions.db"


def init_db():
    """Inicializa o banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            color TEXT DEFAULT '#6366f1',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            frequency TEXT NOT NULL CHECK(frequency IN ('monthly', 'yearly')),
            category_id INTEGER NOT NULL,
            next_due_date DATE NOT NULL,
            description TEXT,
            website TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
        )
    """)

    # Insere categorias padrão se não existirem
    default_categories = [
        ("Entretenimento", "#6366f1"),
        ("Trabalho/Produtividade", "#10b981"),
        ("Saúde/Bem-estar", "#ef4444"),
        ("Educação", "#f59e0b"),
        ("Comida", "#ec4899"),
        ("Outros", "#64748b"),
    ]
    for name, color in default_categories:
        cursor.execute("INSERT OR IGNORE INTO categories (name, color) VALUES (?, ?)", (name, color))

    conn.commit()
    conn.close()
    print(f"[DB] Banco inicializado em {DB_PATH}")


async def get_db_connection():
    """Retorna conexão assíncrona com o banco."""
    import aiosqlite
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    return conn


# --- Categories ---

async def get_all_categories() -> list[dict]:
    conn = await get_db_connection()
    async with conn.execute("""
        SELECT c.id, c.name, c.color, COUNT(s.id) as subscription_count
        FROM categories c
        LEFT JOIN subscriptions s ON c.id = s.category_id AND s.is_active = TRUE
        GROUP BY c.id ORDER BY c.name
    """) as cursor:
        rows = await cursor.fetchall()
    await conn.close()
    return [dict(r) for r in rows]


async def create_category(name: str, color: str = "#6366f1") -> int:
    conn = await get_db_connection()
    try:
        cursor = await conn.execute(
            "INSERT INTO categories (name, color) VALUES (?, ?)", (name, color)
        )
        await conn.commit()
        return cursor.lastrowid
    finally:
        await conn.close()


async def update_category(category_id: int, name: str, color: str):
    conn = await get_db_connection()
    await conn.execute(
        "UPDATE categories SET name = ?, color = ? WHERE id = ?", (name, color, category_id)
    )
    await conn.commit()
    await conn.close()


async def delete_category(category_id: int):
    conn = await get_db_connection()
    await conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    await conn.commit()
    await conn.close()


# --- Subscriptions ---

async def get_all_subscriptions(active_only: bool = True) -> list[dict]:
    conn = await get_db_connection()
    where = "WHERE s.is_active = TRUE" if active_only else ""
    today = date.today().isoformat()
    async with conn.execute(f"""
        SELECT s.*, c.name as category_name, c.color as category_color,
               CAST(julianday(s.next_due_date) - julianday('{today}') AS INTEGER) as days_until_due
        FROM subscriptions s
        LEFT JOIN categories c ON s.category_id = c.id
        {where}
        ORDER BY s.next_due_date ASC
    """) as cursor:
        rows = await cursor.fetchall()
    await conn.close()
    return [dict(r) for r in rows]


async def get_subscription_by_id(subscription_id: int) -> Optional[dict]:
    conn = await get_db_connection()
    async with conn.execute("""
        SELECT s.*, c.name as category_name, c.color as category_color
        FROM subscriptions s
        LEFT JOIN categories c ON s.category_id = c.id
        WHERE s.id = ?
    """, (subscription_id,)) as cursor:
        row = await cursor.fetchone()
    await conn.close()
    return dict(row) if row else None


async def create_subscription(data: dict) -> int:
    conn = await get_db_connection()
    try:
        cursor = await conn.execute("""
            INSERT INTO subscriptions (name, price, frequency, category_id, next_due_date, description, website)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data["name"], data["price"], data["frequency"],
            data["category_id"], data["next_due_date"].isoformat(),
            data.get("description"), data.get("website")
        ))
        await conn.commit()
        return cursor.lastrowid
    finally:
        await conn.close()


async def update_subscription(subscription_id: int, updates: dict):
    if not updates:
        return
    conn = await get_db_connection()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [subscription_id]
    await conn.execute(f"UPDATE subscriptions SET {set_clause} WHERE id = ?", values)
    await conn.commit()
    await conn.close()


async def delete_subscription(subscription_id: int):
    conn = await get_db_connection()
    await conn.execute("DELETE FROM subscriptions WHERE id = ?", (subscription_id,))
    await conn.commit()
    await conn.close()


async def toggle_subscription(subscription_id: int):
    conn = await get_db_connection()
    sub = await get_subscription_by_id(subscription_id)
    if sub:
        new_status = not sub["is_active"]
        await conn.execute(
            "UPDATE subscriptions SET is_active = ? WHERE id = ?", (new_status, subscription_id)
        )
        await conn.commit()
    await conn.close()


# --- Stats / Dashboard ---

async def get_dashboard_stats() -> dict:
    conn = await get_db_connection()
    today = date.today()

    # Total mensal (assinaturas ativas)
    async with conn.execute("""
        SELECT 
            SUM(CASE WHEN frequency = 'monthly' THEN price ELSE price / 12 END) as monthly,
            SUM(CASE WHEN frequency = 'yearly' THEN price ELSE price END) as yearly_direct,
            COUNT(*) as total,
            COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active
        FROM subscriptions
    """) as cursor:
        stats_row = await cursor.fetchone()

    monthly = stats_row[0] or 0
    yearly_total = (stats_row[1] or 0) + (monthly * 12)

    # Próximos vencimentos (próximos 30 dias)
    from datetime import timedelta as _td
    thirty_days_later = (today + _td(days=30)).isoformat()

    async with conn.execute("""
        SELECT s.id, s.name, s.price, s.frequency, s.next_due_date,
               c.name as category_name, c.color as category_color,
               CAST(julianday(s.next_due_date) - julianday(?) AS INTEGER) as days_until
        FROM subscriptions s
        LEFT JOIN categories c ON s.category_id = c.id
        WHERE s.is_active = TRUE AND s.next_due_date BETWEEN ? AND ?
        ORDER BY s.next_due_date ASC
        LIMIT 10
    """, (today.isoformat(), today.isoformat(), thirty_days_later)) as cursor:
        upcoming_rows = await cursor.fetchall()

    # Top categoria por gasto
    async with conn.execute("""
        SELECT c.name, c.color,
               SUM(CASE WHEN s.frequency = 'monthly' THEN s.price ELSE s.price / 12 END) as monthly_spend
        FROM subscriptions s
        JOIN categories c ON s.category_id = c.id
        WHERE s.is_active = TRUE
        GROUP BY c.id
        ORDER BY monthly_spend DESC
        LIMIT 1
    """) as cursor:
        top_cat = await cursor.fetchone()

    await conn.close()

    return {
        "total_monthly_spending": round(monthly, 2),
        "total_yearly_spending": round(yearly_total, 2),
        "upcoming_renewals": [dict(r) for r in upcoming_rows],
        "top_category": top_cat[0] if top_cat else None,
        "top_category_spending": round(top_cat[2], 2) if top_cat else 0.0,
        "active_subscriptions": stats_row[3],
        "total_subscriptions": stats_row[2],
    }
