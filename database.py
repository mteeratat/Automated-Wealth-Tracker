from peewee import (
    SqliteDatabase,
    Model,
    DateField,
    CharField,
    FloatField,
    DateTimeField,
    CompositeKey,
)
from supabase import create_client, Client
import datetime
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# 🔑 Supabase SDK Configuration (Preferred for Cloud)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase: Client = None
if SUPABASE_URL and SUPABASE_ANON_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# 🧠 Peewee Configuration (Local Fallback)
# We keep Peewee for local SQLite development. It's great for testing!
db_name = os.getenv("DB_NAME", "wealth.db")
db = SqliteDatabase(db_name)

if supabase:
    # If using Supabase SDK (HTTPS), we use a dummy DB for Peewee models
    # to avoid creating a local file unless necessary.
    db = SqliteDatabase(":memory:")
else:
    db = SqliteDatabase(db_name)


class AssetPrice(Model):
    date = DateField(default=datetime.date.today)
    asset_name = CharField()
    price = FloatField()
    currency = CharField(default="USD")
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
        primary_key = CompositeKey("date", "asset_name")


def init_db():
    if not supabase:
        db.connect()
        db.create_tables([AssetPrice])


def save_asset_price(date, asset_name, price, currency):
    """Saves asset price using Supabase SDK (HTTPS) or Peewee (PostgreSQL/SQLite)."""
    if supabase:
        # Use Supabase Python Client (HTTPS - Port 443)
        # We use upsert to handle idempotency. Supabase needs a unique constraint
        # on (date, asset_name) for this to work perfectly as get_or_create.
        data = {
            "date": str(date),
            "asset_name": asset_name,
            "price": price,
            "currency": currency,
            "updated_at": datetime.datetime.now().isoformat(),
        }
        # Attempt to insert, ignore if duplicate (idempotency)
        try:
            res = (
                supabase.table("assetprice")
                .upsert(data, on_conflict="date,asset_name")
                .execute()
            )
            return True, len(res.data) > 0
        except Exception as e:
            # If the table doesn't exist yet, we might need to handle it
            # But usually you create the table in the UI first with Supabase
            logger.error(f"Supabase SDK Error: {e}")
            raise e
    else:
        # Fallback to Peewee ORM
        # In Peewee, we use get_or_create then manual update if we want updated_at to refresh
        obj, created = AssetPrice.get_or_create(
            date=date,
            asset_name=asset_name,
            defaults={
                "price": price,
                "currency": currency,
                "updated_at": datetime.datetime.now(),
            },
        )
        if not created:
            obj.price = price
            obj.updated_at = datetime.datetime.now()
            obj.save()
        return True, created


def fetch_asset_prices():
    """Fetches all prices sorted by date descending."""
    if supabase:
        res = (
            supabase.table("assetprice").select("*").order("date", desc=True).execute()
        )
        return res.data
    else:
        query = AssetPrice.select().order_by(AssetPrice.date.desc())
        return list(query.dicts())
