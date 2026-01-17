from peewee import *
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

db = SqliteDatabase(os.getenv("DB_NAME", "wealth.db"))

class AssetPrice(Model):
    date = DateField(default=datetime.date.today)
    asset_name = CharField()
    price = FloatField()
    currency = CharField(default='USD')

    class Meta:
        database = db
        indexes = (
            (('date', 'asset_name'), True),
        )

def init_db():
    db.connect()
    db.create_tables([AssetPrice])
