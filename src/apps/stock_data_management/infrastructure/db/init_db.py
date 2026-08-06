from apps.stock_data_management.infrastructure.db.session import mysql_engine, postgres_engine
from core.models.base import MySQLBase, PostgresBase
import apps.stock_data_management.models


def create_tables():
    MySQLBase.metadata.create_all(bind=mysql_engine)
    PostgresBase.metadata.create_all(bind=postgres_engine)


if __name__ == "__main__":
    create_tables()
    print("Tables Created")
