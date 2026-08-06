from apps.stock_data_management.config.settings import settings
from core.infrastructure.database.sql_database.engine import create_db_engine
from core.infrastructure.database.sql_database.session import create_session_factory
from sqlalchemy.orm import Session, sessionmaker


mysql_engine = create_db_engine(
    settings.STOCK_INFO_MYSQL_DATABASE_URI,
    {
        "local_infile": True
    }
)

MySQLSessionFactory: sessionmaker[Session] = create_session_factory(
    mysql_engine
)


postgres_engine = create_db_engine(
    settings.STOCK_INFO_POSTGRES_DATABASE_URI
)

PostgresSessionFactory: sessionmaker[Session] = create_session_factory(
    postgres_engine
)
