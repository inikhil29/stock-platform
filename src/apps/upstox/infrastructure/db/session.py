

from apps.upstox.config.settings import (
    settings
)
from core.database.mysql.engine import create_db_engine
from core.database.mysql.session import create_session_factory


engine = create_db_engine(
    settings.UPSTOX_DATABASE_URL
)

SessionFactory = create_session_factory(
    engine
)