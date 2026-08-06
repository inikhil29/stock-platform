from sqlalchemy import create_engine


def create_db_engine(
    connection_string: str,
    connect_args:dict = {}
):

    return create_engine(
        connection_string,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=1800,
        echo=False,
        connect_args= connect_args
    )
