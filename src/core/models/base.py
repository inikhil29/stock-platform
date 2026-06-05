from sqlalchemy.orm import (
    DeclarativeBase
)


class Base(DeclarativeBase):

    def to_dict(self):

        result = {}

        for column in self.__table__.columns:

            value = getattr(
                self,
                column.name
            )

            result[column.name] = value

        return result
