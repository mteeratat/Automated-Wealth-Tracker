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

# 1. SETUP & ENVIRONMENT
load_dotenv()
logger = logging.getLogger(__name__)

# 🔑 Supabase SDK Configuration
# This is our "Production Path". It uses HTTPS (Port 443) to talk to the Cloud.
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Initialize the Supabase Client if credentials are provided in .env
supabase: Client = None
if SUPABASE_URL and SUPABASE_ANON_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# 🧠 Peewee Configuration (The "Dual-Mode" Strategy)
# We use SQLite for local development so you can work without internet.
db_name = os.getenv("DB_NAME", "wealth.db")

if supabase:
    # DESIGN CHOICE: In-Memory Database
    # If we are using Supabase Cloud, we don't need a local wealth.db file.
    # We use ":memory:" to keep Peewee happy without creating junk files.
    db = SqliteDatabase(":memory:")
else:
    # Stick to a real local file if Cloud keys are missing.
    db = SqliteDatabase(db_name)


class AssetPrice(Model):
    """
    The Blueprint: Defines the columns in our 'assetprice' table.
    Ensures data consistency across both SQLite and Supabase.
    """
    date = DateField(default=datetime.date.today)
    asset_name = CharField()
    price = FloatField()
    currency = CharField(default="USD")
    # Audit Field: Tracks exactly when the record was last touched
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
        # CRITICAL SRE FEATURE: The Composite Key
        # Prevents duplicate entries for the same stock on the same day.
        # This makes the 'Upsert' logic possible.
        primary_key = CompositeKey("date", "asset_name")


def init_db():
    """
    Checks if a local database needs to be created.
    If using Supabase, usually the table is created in the Supabase UI.
    """
    if not supabase:
        db.connect()
        db.create_tables([AssetPrice])


def save_asset_price(date, asset_name, price, currency):
    """
    The Adapter Function: Routes data to the correct storage engine.
    This handles the complexity so tracker.py doesn't have to.
    """
    if supabase:
        # PATH A: Supabase SDK (HTTPS)
        # We use .upsert() which means 'Update if exists, else Insert'.
        data = {
            "date": str(date),
            "asset_name": asset_name,
            "price": price,
            "currency": currency,
            "updated_at": datetime.datetime.now().isoformat(),
        }
        try:
            res = (
                supabase.table("assetprice")
                .upsert(data, on_conflict="date,asset_name")
                .execute()
            )
            # Returns True and whether a new record was processed
            return True, len(res.data) > 0
        except Exception as e:
            logger.error(f"Supabase SDK Error: {e}")
            raise e
    else:
        # PATH B: Peewee ORM (Local SQLite)
        # Handle idempotency manually for SQLite
        obj, created = AssetPrice.get_or_create(
            date=date,
            asset_name=asset_name,
            defaults={
                "price": price,
                "currency": currency,
                "updated_at": datetime.datetime.now(),
            },
        )
        # If the record already existed, we update the price to the latest
        if not created:
            obj.price = price
            obj.updated_at = datetime.datetime.now()
            obj.save()
        return True, created


def fetch_asset_prices():
    """
    Data Retrieval Layer: Pulls history for the Streamlit Dashboard.
    Always returns data sorted by most recent date first.
    """
    if supabase:
        # Fetch from Supabase Cloud
        res = (
            supabase.table("assetprice").select("*").order("date", desc=True).execute()
        )
        return res.data
    else:
        # Fetch from Local SQLite File
        query = AssetPrice.select().order_by(AssetPrice.date.desc())
        return list(query.dicts())
