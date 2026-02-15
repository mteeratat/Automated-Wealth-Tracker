from peewee import (
    SqliteDatabase,
    PostgresqlDatabase,
    Model,
    DateField,
    CharField,
    FloatField,
    CompositeKey,
)
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# 🧠 Dynamic Database Choice
if os.getenv("DB_TYPE") == "postgres":
    db = PostgresqlDatabase(
        os.getenv("POSTGRES_DB", "wealth_db"),
        user=os.getenv("POSTGRES_USER", "user"),
        password=os.getenv("POSTGRES_PASSWORD", "password"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
    )
else:
    db = SqliteDatabase(os.getenv("DB_NAME", "wealth.db"))


class AssetPrice(Model):
    date = DateField(default=datetime.date.today)
    asset_name = CharField()
    price = FloatField()
    currency = CharField(default="USD")

    class Meta:
        database = db
        primary_key = CompositeKey("date", "asset_name")


def init_db():
    db.connect()
    db.create_tables([AssetPrice])
