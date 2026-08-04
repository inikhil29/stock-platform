from apps.stock_info.config.settings import settings
from core.infrastructure.database.sql_database.engine import create_db_engine
from core.infrastructure.database.sql_database.session import create_session_factory
from sqlalchemy.orm import Session, sessionmaker


mysql_engine = create_db_engine(
    settings.UPSTOX_MYSQL_DATABASE_URI
)

MySQLSessionFactory:sessionmaker[Session] = create_session_factory(
    mysql_engine
)



postgres_engine = create_db_engine(
    settings.UPSTOX_POSTGRES_DATABASE_URI
)

PostgresSessionFactory = create_session_factory(
    postgres_engine
)
