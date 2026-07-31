from sqlalchemy.orm import (
    DeclarativeBase
)


class MySQLBase(DeclarativeBase):

    def to_dict(self):

        result = {}

        for column in self.__table__.columns:

            value = getattr(
                self,
                column.name
            )

            result[column.name] = value

        return result



class PostgresBase(DeclarativeBase):

    def to_dict(self):

        result = {}

        for column in self.__table__.columns:

            value = getattr(
                self,
                column.name
            )

            result[column.name] = value

        return result