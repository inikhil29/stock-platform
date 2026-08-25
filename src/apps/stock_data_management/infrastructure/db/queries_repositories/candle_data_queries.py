"""
Candle Data Queries Repository Module.

Provides custom analytical queries across historical candlestick data and raw batch info in PostgreSQL.
"""

from sqlalchemy.orm import Session


class CandleDataQueries:
    """
    Query repository for custom multi-table candlestick calculations and aggregations.

    Attributes:
        _session (Session): Active SQLAlchemy database session.
    """

    def __init__(self, session: Session):
        """
        Initialize CandleDataQueries with an active database session.

        Parameters:
            session (Session): Active SQLAlchemy session bound to a transaction.
        """
        self._session = session
