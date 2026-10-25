"""Duplicate field names must be rejected instead of silently colliding."""

import pytest
from pydantic import ValidationError

from fastdocparse.schema import Field, Schema


def test_duplicate_field_names_are_invalid():
    with pytest.raises(ValidationError, match="unique"):
        Schema(name="Invoice", fields=[
            Field(name="total", description="net total"),
            Field(name="total", description="gross total"),
        ])


def test_unique_fields_preserve_original_order():
    schema = Schema(name="Invoice", fields=[
        Field(name="number", description="invoice number"),
        Field(name="total", description="amount"),
    ])
    assert [field.name for field in schema.fields] == ["number", "total"]


def test_reserved_meta_name_still_rejected():
    with pytest.raises(ValidationError, match="reserved"):
        Schema(name="Invoice", fields=[Field(name="_meta", description="metadata")])
