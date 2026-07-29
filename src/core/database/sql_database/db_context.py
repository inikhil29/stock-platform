from contextlib import contextmanager


@contextmanager
def transaction(
    session_factory
):

    session = session_factory()

    try:

        yield session

        session.commit()

    except Exception:

        session.rollback()

        raise

    finally:

        session.close()