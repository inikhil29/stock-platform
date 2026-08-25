"""
Unit tests for Core Polars DataFrame engine.
"""

import json
from pathlib import Path
import polars as pl
from sqlalchemy import BigInteger, Float, Integer, String

from core.dataframe.engines.polars.dataframe import PolarsDataFrame
from core.dataframe.engines.polars.reader import PolarsReader
from core.dataframe.engines.polars.schema_validator import PolarsSchemaValidator
from core.dataframe.engines.polars.writer import PolarsDataWriter


class TestPolarsDataFrameEngine:
    """Test suite for Polars Reader, Writer, and Schema Validator."""

    def test_polars_reader_csv(self, tmp_path: Path):
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("a,b\n1,foo\n2,bar\n")

        reader = PolarsReader()
        df = reader.read_csv(str(csv_file))

        assert isinstance(df, PolarsDataFrame)
        assert df.native.shape == (2, 2)
        assert df.native["a"].to_list() == [1, 2]

    def test_polars_reader_json(self, tmp_path: Path):
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps([{"a": 1, "b": "foo"}, {"a": 2, "b": "bar"}]))

        reader = PolarsReader()
        df = reader.read_json(str(json_file))

        assert isinstance(df, PolarsDataFrame)
        assert df.native.shape == (2, 2)

    def test_polars_writer_csv_and_parquet(self, tmp_path: Path):
        native_df = pl.DataFrame({"symbol": ["RELIANCE", "TCS"], "price": [2900.0, 3800.0]})
        df = PolarsDataFrame(native_df)

        writer = PolarsDataWriter()
        csv_out = tmp_path / "out.csv"
        parquet_out = tmp_path / "out.parquet"

        writer.write_csv(df, str(csv_out))
        assert csv_out.exists()

        writer.write_parquet(df, str(parquet_out))
        assert parquet_out.exists()

    def test_polars_schema_validator_type_mapping(self):
        validator = PolarsSchemaValidator()
        assert validator.TYPE_MAPPING[Integer] == pl.Int64
        assert validator.TYPE_MAPPING[String] == pl.String
        assert validator.TYPE_MAPPING[Float] == pl.Float64

    def test_polars_schema_validator_apply(self):
        validator = PolarsSchemaValidator()
        native_df = pl.DataFrame({
            "id": ["1", "2"],
            "name": ["A", "B"],
            "extra_col": [True, False]
        })
        df = PolarsDataFrame(native_df)

        schema = {
            "id": Integer(),
            "name": String(50)
        }

        validated = validator.apply(df, schema)
        assert "extra_col" not in validated.native.columns
        assert set(validated.native.columns) == {"id", "name"}
        assert validated.native.schema["id"] == pl.Int64
        assert validated.native.schema["name"] == pl.String

