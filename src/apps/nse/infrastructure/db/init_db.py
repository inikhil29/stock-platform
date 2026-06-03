from core.models.base import Base
from core.database.mysql.engine import upstox_db_engine


def create_tables():
    Base.metadata.create_all(bind=upstox_db_engine) 
    
if __name__ == "__main__":
    create_tables()
    print("Tables Created")