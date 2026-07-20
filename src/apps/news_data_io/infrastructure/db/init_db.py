from apps.nse.infrastructure.db.session import engine
from core.models.base import Base
import apps.upstox.models


def create_tables():
    Base.metadata.create_all(bind=engine) 
    
if __name__ == "__main__":
    create_tables()
    print("Tables Created")