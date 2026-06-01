from sqlalchemy.orm import sessionmaker


def create_session_factory(
    engine
):

    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False
    )