from apps.nse.config.settings import settings
from core.database.sql_database.engine import create_db_engine
from core.database.sql_database.session import create_session_factory


mysql_engine = create_db_engine(
    settings.NSE_MYSQL_DATABASE_URI
)

MySQLSessionFactory = create_session_factory(
    mysql_engine
)
