from apps.stock_info.infrastructure.db.session import mysql_engine, postgres_engine
from core.models.base import MySQLBase
import apps.stock_info.models


def create_tables():
    MySQLBase.metadata.create_all(bind=mysql_engine)


if __name__ == "__main__":
    create_tables()
    print("Tables Created")
