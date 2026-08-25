"""
Unit tests for Core Base Repositories (PostgreSQL, MongoDB, MySQL).
"""

from typing import ClassVar
from unittest.mock import MagicMock
import pytest
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

from core.repositories.base_mongo_repository import BaseMongoRepository
from core.repositories.base_mysql_repository import BaseMySQLRepository
from core.repositories.base_postgres_repository import BasePostgresRepository

OrmBase = declarative_base()


class SampleModel(OrmBase):
    __tablename__ = "sample_table"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    code = Column(String(20))

    def to_dict(self):
        return {"id": self.id, "name": self.name, "code": self.code}


class SampleDocModel(BaseModel):
    _collection_name: ClassVar[str] = "sample_collection"
    _indexes: ClassVar[list] = [{"fields": [("code", 1)], "unique": True}]
    name: str
    code: str


class ConcretePostgresRepo(BasePostgresRepository[SampleModel]):
    _model = SampleModel


class TestBasePostgresRepository:
    """Test suite for generic BasePostgresRepository operations."""

    def test_insert_one(self, mock_db_session):
        repo = ConcretePostgresRepo(session=mock_db_session)
        result = repo.insert_one({"name": "Test Entity", "code": "TST"})

        assert isinstance(result, SampleModel)
        assert result.name == "Test Entity"
        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_called_once()

    def test_find_by_id(self, mock_db_session):
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_obj = SampleModel(id=1, name="Test", code="TST")
        mock_query.filter.return_value.first.return_value = mock_obj

        repo = ConcretePostgresRepo(session=mock_db_session)
        result = repo.find_by_id(1)
        assert result == mock_obj

    def test_find_one(self, mock_db_session):
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_obj = SampleModel(id=1, name="Test", code="TST")
        mock_query.filter_by.return_value.first.return_value = mock_obj

        repo = ConcretePostgresRepo(session=mock_db_session)
        result = repo.find_one({"code": "TST"})
        assert result == {"id": 1, "name": "Test", "code": "TST"}

    def test_find_many(self, mock_db_session):
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_obj = SampleModel(id=1, name="Test", code="TST")
        mock_query.offset.return_value.limit.return_value.all.return_value = [mock_obj]

        repo = ConcretePostgresRepo(session=mock_db_session)
        result = repo.find_many()
        assert result == [mock_obj]

    def test_update_one(self, mock_db_session):
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter_by.return_value.update.return_value = 1

        repo = ConcretePostgresRepo(session=mock_db_session)
        count = repo.update_one({"id": 1}, {"name": "Updated"})
        assert count == 1

    def test_delete_one(self, mock_db_session):
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter_by.return_value.delete.return_value = 1

        repo = ConcretePostgresRepo(session=mock_db_session)
        count = repo.delete_one({"id": 1})
        assert count == 1

    def test_get_valid_columns(self, mock_db_session):
        repo = ConcretePostgresRepo(session=mock_db_session)
        cols = repo.get_valid_columns()
        assert "name" in cols
        assert "code" in cols
        assert "id" in cols

    def test_bulk_upsert_empty(self, mock_db_session):
        repo = ConcretePostgresRepo(session=mock_db_session)
        assert repo.bulk_upsert([]) == 0


class TestBaseMongoRepository:
    """Test suite for generic BaseMongoRepository operations."""

    def test_insert_one(self):
        mock_db = MagicMock()
        mock_coll = MagicMock()
        mock_db.__getitem__.return_value = mock_coll
        mock_coll.insert_one.return_value = MagicMock(inserted_id="507f1f77bcf86cd799439011")

        repo = BaseMongoRepository(database=mock_db, model_class=SampleDocModel)
        inserted_id = repo.insert_one({"name": "Doc1", "code": "D1"})

        assert inserted_id == "507f1f77bcf86cd799439011"
        mock_coll.insert_one.assert_called_once()

    def test_insert_many(self):
        mock_db = MagicMock()
        mock_coll = MagicMock()
        mock_db.__getitem__.return_value = mock_coll
        mock_coll.insert_many.return_value = MagicMock(inserted_ids=["id1", "id2"])

        repo = BaseMongoRepository(database=mock_db, model_class=SampleDocModel)
        ids = repo.insert_many([{"name": "Doc1", "code": "D1"}, {"name": "Doc2", "code": "D2"}])

        assert ids == ["id1", "id2"]

    def test_upsert_one(self):
        mock_db = MagicMock()
        mock_coll = MagicMock()
        mock_db.__getitem__.return_value = mock_coll

        repo = BaseMongoRepository(database=mock_db, model_class=SampleDocModel)
        repo.upsert_one({"code": "D1"}, {"name": "Doc1", "code": "D1"})

        mock_coll.update_one.assert_called_once()


class TestBaseMySQLRepository:
    """Test suite for generic BaseMySQLRepository operations."""

    def test_insert_one(self, mock_db_session):
        repo = BaseMySQLRepository(model=SampleModel, session=mock_db_session)
        obj = repo.insert_one({"name": "MySQL Entity", "code": "M1"})

        assert isinstance(obj, SampleModel)
        mock_db_session.add.assert_called_once()

    def test_find_by_id(self, mock_db_session):
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = SampleModel(id=1, name="Test")

        repo = BaseMySQLRepository(model=SampleModel, session=mock_db_session)
        result = repo.find_by_id(1)

        assert result.id == 1

    def test_bulk_upsert_empty(self, mock_db_session):
        repo = BaseMySQLRepository(model=SampleModel, session=mock_db_session)
        assert repo.bulk_upsert([]) == 0


