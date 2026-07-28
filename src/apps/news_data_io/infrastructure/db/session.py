from apps.nse.config.settings import settings
from core.database.mysql.mysql_engine import create_db_engine
from core.database.mysql.session import create_session_factory


mysql_engine = create_db_engine(
    settings.NSE_MYSQL_DATABASE_URL
)

MySQLSessionFactory = create_session_factory(
    mysql_engine
)
