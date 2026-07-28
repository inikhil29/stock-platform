from apps.upstox.infrastructure.db.session import mysql_engine
from core.models.base import Base
import apps.upstox.models


def create_tables():
    Base.metadata.create_all(bind=mysql_engine)


if __name__ == "__main__":
    create_tables()
    print("Tables Created")
